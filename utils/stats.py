import math
import numpy


def avg(lis, exception=0.0, cycles=False):
    """
    Shamelessly stolen almost verbatim from 1678
    Copyright (c) 2019 FRC Team 1678: Citrus Circuits

    Calculates the average of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        return round(sum(lis) / len(lis), 1)


def maximum(lis, exception=0.0, cycles=False):
    """
    Shamelessly stolen almost verbatim from 1678
    Copyright (c) 2019 FRC Team 1678: Citrus Circuits

    Calculates the average of a list.

    lis is the list that is averaged.
    exception is returned if there is a divide by zero error. The
    default is 0.0 because the main usage in in percentage calculations.
    """
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        return round(max(lis))


def p75(lis, exception=0.0, cycles=False):
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        lis.sort()
        # If the cycles argument is true, it takes the lower half of
        # the list, which are the faster cycle times.
        if cycles is True:
            # 'math.ceil()' rounds the float up to be an int.
            upper_half = lis[:math.ceil(len(lis) / 2)]
        else:
            # 'math.floor()' rounds the float down to be an int.
            upper_half = lis[-math.floor(len(lis) / 2):]
        return round(sum(upper_half) / len(upper_half), 1)


def SD(lis, exception=0.0, cycles=False):
    """Calculates the standard deviation of a list.

        lis is the list that the standard deviation is taken of.
        exception is returned if there is a divide by zero error. The
        default is 0.0 because if there is no data, there is no deviation.
        """
    lis = [item for item in lis if item is not None]
    if len(lis) == 0:
        return exception
    else:
        return round(float(numpy.std(lis)), 1)


def percent_success_shooting(timds, time, action, *types):
    successes = total_filter_values((filter_timeline_actions([timd for timd in timds], actionType=action, actionTime=time)), *types)
    fails = total_filter_values((filter_timeline_actions([timd for timd in timds], actionType=action, actionTime=time)), 'misses')

    if successes + fails == 0:
        return 0

    return round(100 * (successes/(successes+fails)))


def true_offensive_contribution(timd):
    total_contribution = 0
    if timd['header'].get('leftLine'):
        total_contribution += 5
    for action in timd.get('timeline', []):
        if action.get('actionType') == 'shoot' and action.get('actionTime') == 'teleop':
            total_contribution += action.get('lowerGoal') * 1
            total_contribution += action.get('outerPort') * 2
            total_contribution += action.get('innerPort') * 3
        elif action.get('actionType') == 'shoot' and action.get('actionTime') == 'auto':
            total_contribution += action.get('lowerGoal') * 2
            total_contribution += action.get('outerPort') * 4
            total_contribution += action.get('innerPort') * 6
        elif action.get('actionType') == 'wheel':
            if action.get('wheelType') == 'rotationControl':
                total_contribution += 10
            elif action.get('wheelType') == 'positionControl':
                total_contribution += 20
        elif action.get('actionType') == 'climb':
            if action.get('climbHeight') == 'parked':
                total_contribution += 5
            elif action.get('climbHeight') == 'hanging':
                if action.get('levelClimb'):
                    total_contribution += 40
                else:
                    total_contribution += 25

    return total_contribution


def sum_sd(SDs):
    return sum(map(lambda x: x ** 2 , filter(lambda s: s != None, SDs))) ** 0.5


def percent_difference(num1, num2):
    return (num1-num2) / avg([num1, num2])


def filter_timeline_actions(timds, **filters):
    filtered_timeline = []
    # For each action, if any of the specifications are not met, the
    # loop breaks and moves on to the next action, but if all the
    # specifications are met, the action is added to the filtered
    # timeline.
    for timd in timds:
        for action in timd.get('timeline', []):
            for data_field, requirement in filters.items():
                if action.get(data_field) != requirement:
                    break
            # If all the requirements are met, the action is added to the
            # (returned) filtered timeline.
            else:
                filtered_timeline.append(action)
    return filtered_timeline


def total_filter_values(filtered_timeline, *data_fields):
    total = 0
    for shot in filtered_timeline:
        for data_field in data_fields:
            total += shot[data_field]
    return total
