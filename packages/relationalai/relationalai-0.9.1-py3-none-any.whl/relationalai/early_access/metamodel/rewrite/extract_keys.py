from __future__ import annotations

from relationalai.early_access.metamodel import ir
from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel.visitor import Visitor, Rewriter
from relationalai.early_access.metamodel.util import OrderedSet
from relationalai.early_access.metamodel import helpers, factory as f, types, builtins
from typing import Optional, Any, Iterable

# Given an Output with a group of keys (some of them potentially null),
# * extract the lookups that bind (transitively) all the keys
# * generate all the valid combinations of keys being present or not
#   * first all keys are present,
#   * then we remove one key at a time,
#   * then we remove two keys at a time,and so on.
#   * the last combination is when all the *nullable* keys are missing.
# * each combination is using the keys to create a compound (hash) key
# * create a Match handling all the cases
# * any key lookup is removed from the original logicals,
#   and is moved at the same level as the Match
# * update the original Output to now use the compound key
#
# E.g., we go from
#
# Logical
#     Foo(foo)
#     rel1(foo, x)
#     Logical ^[v1=None]
#         rel2(foo, v1)
#     Logical ^[v2=None, k2=None]
#         rel3(foo, k2)
#         rel4(k2, v2)
#     Logical ^[v3=None, k3=None]
#         rel5(foo, y)
#         rel6(y, k3)
#         rel7(k3, v3)
#     output[foo, k2, k3](v1, v2, v3)
#
# to
#
# Logical
#     Logical ^[foo, k2=None, k3=None, compound_key]
#         Foo(foo)
#         rel1(foo, x)
#         Match ^[k2=None, k3=None]
#             Logical ^[k2=None, k3=None]
#                 rel3(foo, k2)
#                 rel5(foo, y)
#                 rel6(y, k3)
#             Logical ^[k2=None, k3=None]
#                 rel3(foo, k2)
#                 k3 = None
#             Logical ^[k2=None, k3=None]
#                 rel5(foo, y)
#                 rel6(y, k3)
#                 k2 = None
#             Logical ^[k2=None, k3=None]
#                 k2 = None
#                 k3 = None
#         construct(Hash, "Foo", foo, "Concept2", k2, "Concept3", k3, compound_key)
#     Logical ^[v1=None]
#         rel2(foo, v1)
#     Logical ^[v2=None, k2=None]
#         rel4(k2, v2)
#     Logical ^[v3=None, k3=None]
#         rel7(k3, v3)
#     output[compound_key](v1, v2, v3)

class ExtractKeys(Pass):
    def rewrite(self, model: ir.Model, options:dict={}) -> ir.Model:
        visitor = IdentifyKeysVisitor()
        model.accept(visitor)
        return ExtractKeysRewriter(visitor).walk(model)

class ExtractInfo:
    def __init__(self, vars_to_extract: OrderedSet[ir.Var]):
        self.original_keys = vars_to_extract
        # the subset of the original keys that are nullable or not.
        self.non_nullable_keys: OrderedSet[ir.Var] = OrderedSet()
        self.nullable_keys: OrderedSet[ir.Var] = OrderedSet()
        # lookup tasks that transitively bind all the key vars
        # e.g., if the key is Z, in foo(X, Y), bar(Y, Z), baz(Z, W)
        # we extract foo(X, Y), bar(Y, Z)
        self.key_lookups = []
        # the various match cases handling some of the keys potentially being null.
        self.match_cases = []

class IdentifyKeysVisitor(Visitor):
    def __init__(self):
        self.extract_info_for_logical: dict[ir.Logical, ExtractInfo] = {}
        self.curr_info = None

    def enter(self, node: ir.Node, parent: Optional[ir.Node]=None) -> Visitor:
        if isinstance(node, ir.Logical):
            outputs = [x for x in node.body if isinstance(x, ir.Output) and x.keys]
            if not outputs:
                return self
            assert len(outputs) == 1, "multiple outputs with keys in a logical"
            if not outputs[0].keys:
                return self

            # Logical with an output that has keys
            info = ExtractInfo(OrderedSet.from_iterable(outputs[0].keys))

            # the original keys and any intermediate vars needed to correctly bind the keys
            extended_keys:OrderedSet[ir.Var] = OrderedSet.from_iterable(outputs[0].keys)

            # first, collect all the top-level lookups
            top_level_lookups = []
            for task in node.body:
                if isinstance(task, ir.Lookup):
                    top_level_lookups.append(task)
            key_lookups = self.find_key_lookups_fixpoint(top_level_lookups, extended_keys)

            # then, deal with key lookups inside logicals (with hoisted defaults)
            for task in node.body:
                if isinstance(task, ir.Logical):
                    for h in task.hoisted:
                        if isinstance(h, ir.Default) and h.value is None and h.var in info.original_keys:
                            info.nullable_keys.add(h.var)

                    current_lookups = self.find_key_lookups_fixpoint(task.body, extended_keys)
                    key_lookups.extend(current_lookups)

            info.non_nullable_keys = info.original_keys - info.nullable_keys
            info.key_lookups = key_lookups

            # we only need to transform the logical if there are nullable keys
            if info.nullable_keys:
                self.extract_info_for_logical[node] = info
                self.curr_info = info
        return self

    def leave(self, node: ir.Node, parent: Optional[ir.Node]=None) -> ir.Node:
        if not self.curr_info:
            return node

        if isinstance(node, ir.Aggregate):
            # we assume that variables appearing in aggregate group-by's are not nullable
            for v in node.group:
                if v in self.curr_info.nullable_keys:
                    self.curr_info.nullable_keys.remove(v)
        elif isinstance(node, ir.Logical) and node in self.extract_info_for_logical:
            # if the set of nullable keys became empty, we shouldn't attempt to transform the logical
            if not self.curr_info.nullable_keys:
                self.extract_info_for_logical.pop(node)
            self.curr_info = None

        return node

    def find_key_lookups_fixpoint(self, tasks:Iterable[ir.Task], keys:OrderedSet[ir.Var]):
        # lookups with a single argument correspond to concepts.
        # we should keep them ahead of the other lookups.
        concept_lookups = []
        # for lookups with multiple arguments, we start from those that have a key as the last
        # argument and move backwards. that's why each time we insert at the front of the list
        lookups = []

        there_is_progress = True
        while there_is_progress:
            there_is_progress = False
            for task in tasks:
                if isinstance(task, ir.Lookup) and task not in lookups and task not in concept_lookups:
                    vars = helpers.vars(task.args)
                    if len(vars) == 1 and vars[0] in keys:
                        concept_lookups.append(task)
                        there_is_progress = True
                    elif len(vars) > 1 and all(v in keys for v in vars[1:]):
                        assert isinstance(vars[0], ir.Var)
                        keys.add(vars[0])
                        lookups.insert(0, task)
                        there_is_progress = True

        return concept_lookups + lookups

class ExtractKeysRewriter(Rewriter):
    def __init__(self, visitor: IdentifyKeysVisitor):
        super().__init__()
        self.visitor = visitor

    def handle_logical(self, node: ir.Logical, parent: ir.Node, ctx:Optional[Any]=None) -> ir.Logical:
        new_body = self.walk_list(node.body, node)

        # We are in a logical with an output at this level.
        if node in self.visitor.extract_info_for_logical:
            info = self.visitor.extract_info_for_logical[node]

            # create a subset of the key lookups, if all the nullable keys are null.
            # this will be used at the top-level outside the Match.
            # they should also be removed from each Match case.
            key_lookups = list(info.key_lookups)
            # create a copy of the non-nullable keys so we can modify it
            non_nullable_keys = OrderedSet.from_iterable(info.nullable_keys) - OrderedSet.from_iterable(info.non_nullable_keys)

            self._remove_key_lookups(key_lookups, non_nullable_keys, info.non_nullable_keys)

            # create a compound key that will be used in place of the original keys.
            compound_key = f.var("compound_key", types.Hash)

            hoisted:list[ir.VarOrDefault] = [ir.Default(v, None) for v in info.nullable_keys]
            self._nullable_key_combinations(info, [], 0, compound_key, hoisted, key_lookups)

            key_match = f.match(info.match_cases, hoisted)
            key_lookups.append(key_match)

            # create the arguments to hash
            values: list[ir.Value] = [compound_key.type]
            for key in info.original_keys:
                assert isinstance(key.type, ir.ScalarType)
                values.append(ir.Literal(types.String, key.type.name))
                values.append(key)
            key_lookups.append(ir.Construct(
                None,
                tuple(values),
                compound_key,
                OrderedSet().frozen()
            ))

            key_logical = f.logical(tuple(key_lookups), list(info.non_nullable_keys) + hoisted + [compound_key])

            final_body:list[ir.Task] = [key_logical]
            for task in new_body:
                if task in info.key_lookups:
                    continue

                if isinstance(task, ir.Logical):
                    task = self._clean_logical(task, info)
                    # after the cleanup, the logical came up empty
                    if not task:
                        continue

                if isinstance(task, ir.Output):

                    final_body.append(f.output(list(task.aliases), [compound_key], annos=list(task.annotations)))
                else:
                    final_body.append(task)
            return f.logical(final_body, node.hoisted)
        else:
            return node if new_body is node.body else f.logical(new_body, node.hoisted)

    def _nullable_key_combinations(
            self,
            info: ExtractInfo,
            nullable_non_null_keys: list[ir.Var],
            idx: int,
            compound_key: ir.Var,
            hoisted: list[ir.VarOrDefault],
            lookups_to_purge: list[ir.Task]):

        if idx < len(info.nullable_keys):
            key = info.nullable_keys[idx]
            self._nullable_key_combinations(info, nullable_non_null_keys + [key], idx + 1, compound_key, hoisted, lookups_to_purge)
            self._nullable_key_combinations(info, nullable_non_null_keys, idx + 1, compound_key, hoisted, lookups_to_purge)
        else:
            self._generate_compound_key_case(info, nullable_non_null_keys, compound_key, hoisted, lookups_to_purge)

    def _generate_compound_key_case(self, info: ExtractInfo, nullable_non_null_keys: list[ir.Var], compound_key: ir.Var, hoisted: list[ir.VarOrDefault], lookups_to_purge: Iterable[ir.Task]):
        key_lookups:list[ir.Task] = []
        for task in info.key_lookups:
            if task not in lookups_to_purge:
                key_lookups.append(task)
        vars_to_purge = OrderedSet.from_iterable(info.nullable_keys) - OrderedSet.from_iterable(nullable_non_null_keys)
        self._remove_key_lookups(key_lookups, vars_to_purge, info.non_nullable_keys)

        # replace a lookup to a key that is NULL, to "key = None"
        for key in info.nullable_keys:
            if key in vars_to_purge:
                key_lookups.append(f.lookup(builtins.eq, [key, None]))

        info.match_cases.append(f.logical(list(key_lookups), hoisted))

    def _remove_key_lookups(self, lookups: list[ir.Task], vars_to_purge: OrderedSet[ir.Var], non_nullable_keys: OrderedSet[ir.Var]):
        there_is_progress = True
        while there_is_progress:
            there_is_progress = False
            for task in lookups:
                assert isinstance(task, ir.Lookup)
                vars = helpers.vars(task.args)
                if vars[-1] in vars_to_purge:
                    lookups.remove(task)
                    new_vars = [v for v in vars if v not in vars_to_purge and v not in non_nullable_keys]
                    vars_to_purge.update(new_vars)
                    there_is_progress = True

    # remove key lookups from logicals, since they are handled in their own dedicated logical
    def _clean_logical(self, node: ir.Logical, info: ExtractInfo):
        new_body = []
        for task in node.body:
            if not(isinstance(task, ir.Lookup) and task in info.key_lookups):
                new_body.append(task)

        if new_body is node.body:
            return node

        if not new_body:
            return None

        new_hoisted = []
        for h in node.hoisted:
            if isinstance(h, ir.Default) and h.value is None and h.var in info.nullable_keys:
                continue
            new_hoisted.append(h)
        return f.logical(new_body, new_hoisted)
