from typing import Dict


def _has_parent_class(obj) -> bool:
    return hasattr(obj, '__class__') and hasattr(obj.__class__, '__bases__') and len(obj.__class__.__bases__) > 0

def serialize_to_dict(obj,class_values:Dict,ignore_null=True):
    def _serialize(value):
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, dict):
            return {k: _serialize(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple, set)):
            return [_serialize(v) for v in value]
        elif hasattr(value, "_as_dict_"):
            return value._as_dict_
        else:
            return str(value)  # fallback for unknown objects

    values_dict = {}
    if _has_parent_class(obj):
        values_dict.update(super(obj.__class__, obj)._as_dict_)
    if class_values:
        values_dict.update(class_values)
        # Serialize and exclude None values

    empty_fields = []
    for key, value in values_dict.items():
        if value is not None:
            values_dict[key] = _serialize(value)
        else:
            empty_fields.append(key)
    
    for key in empty_fields:
            del values_dict[key]
                
    return values_dict