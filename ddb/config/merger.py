from deepmerge import Merger
from deepmerge.strategy.dict import DictStrategies
from deepmerge.strategy.fallback import FallbackStrategies
from deepmerge.strategy.list import ListStrategies
from deepmerge.strategy.type_conflict import TypeConflictStrategies


def _type_conflict_strategy(config, path, base, nxt):
    strategy = TypeConflictStrategies.strategy_override
    if isinstance(nxt, dict):
        if 'merge' in nxt and 'value' in nxt:
            value = nxt['value']
            merge = nxt['merge']
            if isinstance(merge, str):
                if isinstance(value, list) and isinstance(base, list):
                    strategy = ExtendedListStrategies._expand_strategy(merge)  # pylint:disable=protected-access
                    nxt = value
                elif isinstance(value, dict) and isinstance(base, dict):
                    strategy = DictStrategies._expand_strategy(merge)  # pylint:disable=protected-access
                    nxt = value
    return strategy(config, path, base, nxt)


def clean_merge_value_dicts(result):
    """

    :return:
    """

    if isinstance(result, dict):
        updates = []
        for key, value in result.items():
            if isinstance(value, dict) and 'merge' in value and 'value' in value:
                updates.append((key, value['value']))
            elif isinstance(value, list):
                clean_merge_value_dicts(value)
        for key, value in updates:
            result[key] = value

    if isinstance(result, list):
        for elt in result:
            clean_merge_value_dicts(elt)


class ExtendedListStrategies(ListStrategies):
    """
    Custom list strategies
    """

    @staticmethod
    def strategy_append_if_missing(config, path, base, nxt):
        """ use the list nxt. """
        filtered_nxt = [item for item in nxt if item not in base]
        return ListStrategies.strategy_append(config, path, base, filtered_nxt)

    @staticmethod
    def strategy_prepend_if_missing(config, path, base, nxt):
        """ use the list nxt. """
        filtered_nxt = [item for item in nxt if item not in base]
        return ListStrategies.strategy_prepend(config, path, base, filtered_nxt)

    @staticmethod
    def strategy_insert_if_missing(config, path, base, nxt):
        """ use the list nxt. """
        idx = nxt.pop(0)
        filtered_nxt = [item for item in nxt if item not in base]
        if idx >= 0:
            filtered_nxt = list(reversed(filtered_nxt))
        ret = list(base)
        for filtered_nxt_item in filtered_nxt:
            ret.insert(idx, filtered_nxt_item)
        return ret

    @staticmethod
    def strategy_insert(config, path, base, nxt):
        """ use the list nxt. """
        idx = nxt.pop(0)
        ordered_nxt = list(nxt)
        if idx >= 0:
            ordered_nxt = list(reversed(ordered_nxt))
        ret = list(base)
        for ordered_nxt_item in ordered_nxt:
            ret.insert(idx, ordered_nxt_item)
        return ret


def merge_value_strategy_wrapper(strategy):
    """
    Wrap the strategy to remove merge/value dicts if output still have ones.
    """

    def wrapped_strategy(config, path, base, nxt):
        result = strategy(config, path, base, nxt)
        clean_merge_value_dicts(result)
        return result

    return wrapped_strategy


config_merger = Merger(
    [
        (list, merge_value_strategy_wrapper(ListStrategies.strategy_override)),
        (dict, merge_value_strategy_wrapper(DictStrategies.strategy_merge))
    ],
    [merge_value_strategy_wrapper(FallbackStrategies.strategy_override)],
    [_type_conflict_strategy]
)
