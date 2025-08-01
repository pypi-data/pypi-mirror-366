from relationalai.early_access.metamodel import ir as meta
from relationalai.early_access.metamodel import types
from relationalai.early_access.lqp import ir as lqp

def meta_type_to_lqp(typ: meta.Type) -> lqp.PrimitiveType:
    if isinstance(typ, meta.UnionType):
        # By this point, unions can only consist of entity types. In the LQP,
        # they are undifferentiated (hashes), so they all merge.
        assert all(types.is_entity_type(t) for t in typ.types), \
            f"Union type {typ} contains non-entity types: " \
            f"{[t for t in typ.types if not types.is_entity_type(t)]}"

        return lqp.PrimitiveType.UINT128
    else:
        assert isinstance(typ, meta.ScalarType)
        if types.is_builtin(typ):
            if typ == types.Int:
                return lqp.PrimitiveType.INT
            elif typ == types.Float:
                return lqp.PrimitiveType.FLOAT
            elif typ == types.String:
                return lqp.PrimitiveType.STRING
            elif typ == types.Decimal64:
                return lqp.PrimitiveType.DECIMAL64
            elif typ == types.Decimal128:
                return lqp.PrimitiveType.DECIMAL128
            elif typ == types.Date:
                return lqp.PrimitiveType.DATE
            elif typ == types.DateTime:
                return lqp.PrimitiveType.DATETIME
            elif typ == types.RowId:
                return lqp.PrimitiveType.UINT128
            elif typ == types.Number:
                # All types must be specified in the LQP.
                raise Exception("Number type could not be determined.")
            elif types.is_any(typ):
                # All types must be specified in the LQP.
                raise Exception("Type could not be determined.")
            else:
                raise NotImplementedError(f"Unknown builtin type: {typ.name}")
        elif types.is_entity_type(typ):
            return lqp.PrimitiveType.UINT128
        else:
            # Otherwise, the type extends some other type, we use that instead
            assert len(typ.super_types) > 0, f"Type {typ} has no super types"
            assert len(typ.super_types) == 1, f"Type {typ} has multiple super types: {typ.super_types}"
            super_type = typ.super_types[0]
            assert isinstance(super_type, meta.ScalarType), f"Super type {super_type} of {typ} is not a scalar type"
            return meta_type_to_lqp(super_type)

def type_from_constant(arg: lqp.PrimitiveValue) -> lqp.PrimitiveType:
    if isinstance(arg, int):
        return lqp.PrimitiveType.INT
    elif isinstance(arg, float):
        return lqp.PrimitiveType.FLOAT
    elif isinstance(arg, str):
        return lqp.PrimitiveType.STRING
    elif isinstance(arg, lqp.UInt128):
        return lqp.PrimitiveType.UINT128
    else:
        raise NotImplementedError(f"Unknown constant type: {type(arg)}")
