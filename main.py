import plistlib
import struct
import zipfile
import sys
import os.path

def unpack_struct(value: bytes, unit: str = 'f') -> tuple:
    # Convert a string of bytes into either an array of 32-bit floats or ints.
    return struct.unpack(f'{len(value) // 4}{unit}', value)


def chunks(array: list, size: int = 2) -> list:
    # Used to loop over an array of orinates in pairs.
    # Source: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    for i in range(0, len(array), size):
        yield array[i:i + size]


if __name__ == '__main__':
    # Only one argument is accepted, which is the path to the note.
    if len(sys.argv) != 2:
        print(f'Error: Unexpected number of arguments.')
        print(f'Usage: python main.py [example.note]')
        exit()
    
    note_filename = sys.argv[1]

    # Check if we can find the note.
    if not os.path.exists(note_filename):
        print(f'Error: Unable to find {note_filename}.')
        exit()

    with zipfile.ZipFile(note_filename, 'r') as note:
        property_list = None
        
        for name in note.namelist():
            if 'Session.plist' in name:
                with note.open(name, 'r') as session:
                    property_list = plistlib.load(session)
                    break
        
        if property_list == None:
            print(f'Error: Unable to find Session.plist in {note_filename}.')
            exit()

    for item in property_list['$objects']:
        # Since we know the target objects are dicts, we can saftey skiop everything else.
        if type(item) != dict:
            continue

        if 'curvespoints' in item:
            # An array of float co-ordinates which look like (x, y, x, y, x, y, ...)
            curves_points = unpack_struct(value=item['curvespoints'])
        if 'curvesnumpoints' in item:
            # An array of ints that represent each symbol.
            # So each number represents a chunk of curves_points.
            curves_num_points = unpack_struct(
                value=item['curvesnumpoints'], unit='i')
        if 'curveswidth' in item:
            # An array of floats that represent the width of each symbol.
            curves_width = unpack_struct(value=item['curveswidth'])
        if 'curvesfractionalwidths' in item:
            # An array of floats that represent the width of each symbol at the start and end?
            # Not sure.
            curves_fractional_widths = unpack_struct(value=item['curvesfractionalwidths'])

    # Split array of (x, y, x, y, ...) into x = [x, x, x, ...] and y = [y, y, y, ...].
    # This is slower, but simplifies the handling the co-ordinates later.
    # We don't need to iterate in pairs later on.
    x_points = []
    y_points = []
    for (x, y) in chunks(array=curves_points):
        x_points.append(x)
        y_points.append(y)

    # Center the SVG and it should have the bounds of the maximum value of x and y rounded up.
    # This removes clipping of the notes.
    html = [f'<html><body><svg style="margin: auto; display: block" width="{round(max(x_points))}" height="{round(max(y_points))}" xmlns="http://www.w3.org/2000/svg">']
    # Each item in curves_num_points represents the number of co-ordinates a symbol (or curve to be precise) has.
    # We need to keep track of the cumulative number of co-ordinates for each curve so that we 
    # can separate each curve into its own path. This keeps things simple. 
    total_num_points = 0
    for i, num_points in enumerate(curves_num_points):
        # Chunk out the co-ordinates.
        x_sub_points = x_points[total_num_points: total_num_points + num_points]
        y_sub_points = y_points[total_num_points: total_num_points + num_points]
        # An array containing the path commands to draw out a curve.
        commands = []

        # Go through each co-ordinate and convert them into a line command.
        for j in range(len(x_sub_points)):
            if j > 0:
                commands.append(f'M {x_sub_points[j]} {y_sub_points[j]} L {x_sub_points[j - 1]} {y_sub_points[j - 1]}')

        # Build up a list of curves.
        html.append(f'<path d="{" ".join(commands)}" stroke="black" stroke-width="{curves_width[i]}"/>')
        # Keep track of how many co-ordinates we've been through so we can separate out each curve.
        total_num_points += num_points

    # Close off the SVG.
    html.append('</svg></body></html>')

    # Write converted note.
    with open(f'{note_filename.split(".")[0]}.html', 'w') as file:
        file.writelines(html)