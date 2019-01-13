import asyncio
from datetime import datetime
from discord.ext import commands


async def sleep_time(dt: datetime):
    time = (dt - datetime.utcnow()).total_seconds()
    await asyncio.sleep(time)
    return True

all_pil_colors = ['aliceblue', 'antiquewhite', 'aqua', 'aquamarine',
                  'azure', 'beige', 'bisque', 'black', 'blanchedalmond',
                  'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue',
                  'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk',
                  'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray',
                  'darkgrey', 'darkgreen', 'darkkhaki', 'darkmagenta', 'darkolivegreen',
                  'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue',
                  'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
                  'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro',
                  'ghostwhite', 'gold', 'goldenrod', 'gray', 'grey', 'green', 'greenyellow', 'honeydew', 'hotpink',
                  'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon',
                  'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgreen', 'lightgray', 'lightgrey',
                  'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue',
                  'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple',
                  'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise',
                  'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite',
                  'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod',
                  'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue',
                  'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen',
                  'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue',
                  'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen']

pil_colors = ['gold', 'red', 'brown', 'tan', 'teal', 'violet', 'orange', 'crimson', 'aqua', 'cyan', 'darkblue', 'green', 'maroon', 'magenta', 'pink', 'plum', 'purple', 'yellow']


quick_tips = ["uwu is the 2nd version of one of mellows old bots.", "You can only die two times per explore.", "There is an easter egg.", "uwu was made 11/04/18.",
              "uwu has a website you can find it at https://catcastle.xyz!", "Mellowmarshe drew my avatar!", "My creator loves cats and has three!", "Mellowmarshe makes uwu with PyCharm!"]