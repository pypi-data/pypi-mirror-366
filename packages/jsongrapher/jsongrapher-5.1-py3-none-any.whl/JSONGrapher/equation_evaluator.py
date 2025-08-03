from sympy import symbols, Eq, solve, sympify
from pint import UnitRegistry
import re

ureg = UnitRegistry()

def parse_equation(equation_str, variables):
    """
    Parses an equation string by substituting variable names and standalone numbers
    with their magnitudes and formatted units.

    Variable names are replaced with their magnitudes and unit representations, while
    numeric values followed by unit labels are detected and transformed into structured
    unit expressions. Constants without magnitude attributes are substituted directly
    with their values.

    Args:
        equation_str (str): The raw equation containing variable names and/or 
            standalone numeric-unit pairs.
        variables (dict): A dictionary mapping variable names to values. Values
            may be plain constants or Pint quantities with magnitude and units.

    Returns:
        str: A modified equation string in which all applicable values are replaced
            with their corresponding magnitudes and formatted units.

    Example:
        Given `equation_str = "F = m * a + 10 kg"` and 
        `variables = {"m": 5 * ureg.kg, "a": 2 * ureg.m / ureg.s**2}`,
        the result would be:
        `"F = (5 * kilogram) * (2 * meter / second ** 2) + (10 * kilogram)"`
    """
    def detect_and_format_units(equation_str):
        """
        Detects standalone numbers followed by unit symbols within an equation string
        and reformats them into structured magnitude-unit expressions.

        Uses pattern matching to identify numeric-unit pairs (e.g., "10 m") and wraps
        each as "(magnitude * unit)" using Pint for unit interpretation. Supports both
        integer and decimal formats and gracefully ignores invalid conversions.

        Args:
            equation_str (str): A string containing equations with numeric-unit patterns
                such as "3.5 kg", "10 m", or "100s".

        Returns:
            str: The modified equation string with valid numeric-unit pairs replaced
                by formatted expressions like "(3.5 * kilogram)".

        Example:
            detect_and_format_units("10 m + 3.5 kg - 100s")
            # Output: "(10 * meter) + (3.5 * kilogram) - (100 * second)"
        """
        pattern = r"(\d+(\.\d+)?)\s*([a-zA-Z]+)"
        matches = re.findall(pattern, equation_str)
        # Explanation of regular expression parts
        # (\d+(\.\d+)?)
        #     \d+ → Matches one or more digits (e.g., "10", "100", "3").
        #     (\.\d+)? → Matches optional decimal values (e.g., "10.5", "3.14").
        #     This entire part captures numerical values, whether integers or decimals.
        # \s*
        #     Matches zero or more spaces between the number and the unit.
        #     Ensures flexibility in formatting (e.g., "10m" vs. "10 m").
        # ([a-zA-Z]+)
        #     Matches one or more alphabetical characters, capturing the unit symbol.
        #     Ensures that only valid unit names (e.g., "m", "s", "kg") are recognized.
        # Example Matches
        #     "10 m"   → ("10", "", "m")
        #     "3.5 kg" → ("3.5", ".5", "kg")
        #     "100s"   → ("100", "", "s")
        for match in matches:
            magnitude = match[0]  # Extract number
            unit = match[2]  # Extract unit
            try:
                quantity = ureg(f"{magnitude} {unit}")  # Convert to Pint quantity
                formatted_unit = str(quantity.units)
                equation_str = equation_str.replace(f"{magnitude} {unit}", f"({quantity.magnitude} * {formatted_unit})")
            except: #This comment is so that VS code pylint will not flag this line: pylint: disable=bare-except
                pass  # Ignore invalid unit conversions
        return equation_str


    # Sort variable names by length in descending order
    variables_sorted_by_name = sorted(variables.items(), key=lambda x: -len(x[0]))

    # Need to first replace the constants because they could be like "letter e"
    # and could mess up the string after the units are added in.
    # Also need to sort them by length and replace longer ones first because
    # we could have "Ea" and "a", for example.  
    for var_name, var_value in variables_sorted_by_name:  # Removed `.items()`
        if not hasattr(var_value, "magnitude"):  # For constants like "e" with no units  
            equation_str = equation_str.replace(var_name, str(var_value))  # Directly use plain values  

    # Replace variables with their magnitudes and units  
    for var_name, var_value in variables_sorted_by_name:  # Removed `.items()`
        if hasattr(var_value, "magnitude"):  # Ensure it has a magnitude attribute  
            magnitude = var_value.magnitude  
            unit = str(var_value.units)  
            equation_str = equation_str.replace(var_name, f"({magnitude} * {unit})")  

    # Detect and format standalone numbers with units, like "10 m"
    equation_str = detect_and_format_units(equation_str)
    return equation_str

def solve_equation(equation_string, independent_variables_values_and_units, dependent_variable):
    """
    Solves a symbolic equation for a specified dependent variable using the provided
    values and units for independent variables.

    The equation string is transformed into a SymPy expression, with independent
    variables substituted by their corresponding quantities. The function handles
    unit-aware parsing and symbolic manipulation to extract clean, formatted solutions.
    The caret operator (^) is internally replaced with "**" for compatibility with
    Python exponentiation syntax.

    Args:
        equation_string (str): The equation containing a dependent variable and one
            or more independent variables, formatted as a string (e.g., "x * t + y = 10 m").
        independent_variables_values_and_units (dict): Dictionary mapping independent
            variable names to their string-formatted values and units
            (e.g., {"x": "2 m / s", "y": "3 meter"}).
        dependent_variable (str): The name of the variable to solve for.

    Returns:
        list: A list of solution strings, each formatted with magnitude and unit
            separated by a space in parentheses (e.g., ["2.5 (second)", "3.0 (second)"]).
            A well behaved function has single solutions, but some equations can have
            more than one solution, that is why a list is returned.

    Example:
        equation_string = "x * t + y = 10 m"
        independent_variables_values_and_units = {
            "x": "2 m / s",
            "y": "3 meter"
        }
        dependent_variable = "t"

        solve_equation(equation_string, independent_variables_values_and_units, dependent_variable)
        # Output: ["3.5 (second)"]
        # The returned output is a list of solutions.
    """
    # Convert string inputs into Pint quantities
    variables = {name: ureg(value) for name, value in independent_variables_values_and_units.items()}
    independent_variables = list(independent_variables_values_and_units.keys())
    # Explicitly define symbolic variables
    symbols_dict = {var: symbols(var) for var in independent_variables_values_and_units.keys()}
    for var in independent_variables:
        symbols_dict[var] = symbols(var)
    symbols_dict[dependent_variable] = symbols(dependent_variable)

    #change any "^" into "**"
    equation_string = equation_string.replace("^","**")
    # Split the equation into left-hand and right-hand sides
    lhs, rhs = equation_string.split("=")

    # Convert both sides to SymPy expressions
    lhs_sympy = sympify(parse_equation(lhs.strip(), variables), locals=symbols_dict, evaluate=False)
    rhs_sympy = sympify(parse_equation(rhs.strip(), variables), locals=symbols_dict, evaluate=False)

    # Create the equation object
    eq_sympy = Eq(lhs_sympy, rhs_sympy)
    # Solve for the dependent variable
    solutions = solve(eq_sympy, symbols_dict[dependent_variable])
    # Extract magnitude and unit separately from SymPy expressions
    separated_solutions = []
    for sol in solutions:
        magnitude, unit = sol.as_coeff_Mul()  # Works for ANY SymPy expression
        separated_solutions.append((magnitude, unit))

    # Format solutions properly with a space between the magnitude and unit
    formatted_solutions = [f"{mag} ({unit})" for mag, unit in separated_solutions]
    #print(f"Solutions for {dependent_variable} in terms of {independent_variables}: {formatted_solutions}")
    return formatted_solutions


def parse_equation_dict(equation_dict):
    """
    Parses a dictionary containing equation constants and extracts numeric values
    along with their unit labels, if present.

    Each constant in the dictionary is assumed to be a string formatted as either
    "value (units)" or simply "value". The inner `extract_value_units` function handles
    trimming and splitting the string, returning the value and unit separately.
    Constants without a unit are stored with `None` as the unit.

    Args:
        equation_dict (dict): A dictionary mapping constant names to string
            representations of values, optionally followed by units 
            (e.g., {"g": "9.8 (m/s^2)", "pi": "3.1415"}).

    Returns:
        dict: A dictionary mapping each constant name to a list containing two elements:
            the numeric value as a string or float, and the unit as a string or None.

    Example:
        equation_dict = {
            "g": "9.8 (m/s^2)",
            "c": "3.0e8 (m/s)",
            "pi": "3.1415"
        }

        parse_equation_dict(equation_dict)
        # Output: {
        #     "g": ["9.8", "(m/s^2)"],
        #     "c": ["3.0e8", "(m/s)"],
        #     "pi": [3.1415, None]
        # }
    """
    def extract_value_units(entry):
        """
        Separates a numeric value and unit label from a formatted string entry.

        The function trims surrounding whitespace, then splits the string at the first
        space. If both a value and a unit are present, it returns them as separate elements.
        If no unit is found, the numeric portion is converted to a float and returned
        with `None` as the unit.

        Args:
            entry (str): A string containing a numerical value, optionally followed by
                a unit (e.g., "3.5 (kg)", "42").

        Returns:
            list: A list of two elements —
                - value (str or float): The extracted value as a string (if unit present)
                or float (if no unit).
                - unit (str or None): The associated unit string, or None if no unit exists.

        Example:
            extract_value_units("4.2 (m)")
            # Output: ["4.2", "(m)"]

            extract_value_units("100")
            # Output: [100.0, None]
        """
        trimmed_entry = entry.strip()  # Remove leading/trailing whitespace
        split_entry = trimmed_entry.split(" ", 1)  # Split on the first space
        if len(split_entry) > 1:
            value = split_entry[0]
            units = split_entry[1] # Everything after the number
            return [value, units]
        else:
            return [float(split_entry[0]), None]  # Handle constants without units

    def extract_constants(constants_dict):
        """
        Parses a dictionary of constants and extracts their numeric values along with
        any associated unit labels.

        Iterates over each entry in the input dictionary and delegates extraction of
        value-unit pairs to `extract_value_units()`. Handles both constants with units
        (e.g., "3.5 (kg)") and plain numeric values (e.g., "42").

        Args:
            constants_dict (dict): A dictionary mapping constant names to strings
                containing values with optional units.

        Returns:
            dict: A dictionary mapping each constant name to a list with two elements —
                the value and the unit string, or None if no unit is provided.

        Example:
            constants_dict = {
                "R": "8.314 (J/(mol*K))",
                "pi": "3.1415"
            }

            extract_constants(constants_dict)
            # Output: {
            #     "R": ["8.314", "(J/(mol*K))"],
            #     "pi": [3.1415, None]
            # }
        """
        return {
            name: extract_value_units(value)
            for name, value in constants_dict.items()
        }

    def extract_equation(equation_string):
        """
        Extracts a list of variable-like tokens from an input equation string using
        basic pattern matching.

        Uses a regular expression to identify consecutive alphabetic sequences,
        which typically correspond to variable names or function identifiers. All matches
        are returned as a list alongside the original equation.

        Args:
            equation_string (str): A symbolic string expression containing variable names
                (e.g., "E = mc^2", "k = A*exp(-Ea/(R*T))").

        Returns:
            dict: A dictionary with:
                - "equation_string" (str): The original input string.
                - "variables_list" (list): List of extracted alphabetic variable tokens.

        Example:
            extract_equation("k = A * (e ** ((-Ea) / (R * T)))")
            # Output: {
            #     "equation_string": "k = A * (e ** ((-Ea) / (R * T)))",
            #     "variables_list": ["k", "A", "e", "Ea", "R", "T"]
            # }
        """
        variables_list = re.findall(r"([A-Za-z]+)", equation_string)
        return {"equation_string": equation_string, "variables_list": variables_list}

    if 'graphical_dimensionality' in equation_dict:
        graphical_dimensionality = equation_dict['graphical_dimensionality']
    else:
        graphical_dimensionality = 2

    constants_extracted_dict = extract_constants(equation_dict["constants"])
    equation_extracted_dict = extract_equation(equation_dict["equation_string"])
    # x_match = re.match(r"([\w\d{}$/*_°α-ωΑ-Ω]+)\s*\(([\w\d{}$/*_°α-ωΑ-Ω]*)\)", equation_dict["x_variable"])
    # y_match = re.match(r"([\w\d{}$/*_°α-ωΑ-Ω]+)\s*\(([\w\d{}$/*_°α-ωΑ-Ω]*)\)", equation_dict["y_variable"])
    # x_match  = (x_match.group(1), x_match.group(2)) if x_match else (equation_dict["x_variable"], None)
    # y_match = (y_match.group(1), y_match.group(2)) if y_match else (equation_dict["y_variable"], None)
    x_match = extract_value_units(equation_dict["x_variable"])
    y_match = extract_value_units(equation_dict["y_variable"])
    if graphical_dimensionality == 3:
        z_match = extract_value_units(equation_dict["z_variable"])

    # Create dictionaries for extracted variables
    x_variable_extracted_dict = {"label": x_match[0], "units": x_match[1]}
    y_variable_extracted_dict = {"label": y_match[0], "units": y_match[1]}
    if graphical_dimensionality == 3:
        z_variable_extracted_dict = {"label": z_match[0], "units": z_match[1]}

    def prepare_independent_variables(constants_extracted_dict):
        """
        Formats a dictionary of constants into unit-aware strings for independent variable usage.

        Combines numeric values and units into space-separated strings (e.g., "3.5 (kg)")
        suitable for equation parsing and evaluation. If a constant lacks a unit, only
        its value is included.

        Args:
            constants_extracted_dict (dict): Dictionary mapping constant names to a pair —
                a numeric value (str or float) and an optional unit string (str or None).

        Returns:
            dict: A dictionary mapping each constant name to a formatted string suitable
                for unit-aware symbolic substitution.

        Example:
            constants_extracted_dict = {
                "Ea": ["30000", "((J)*(mol^(-1)))"],
                "pi": [3.1415, None]
            }

            prepare_independent_variables(constants_extracted_dict)
            # Output: {
            #     "Ea": "30000 ((J)*(mol^(-1)))",
            #     "pi": "3.1415"
            # }
        """
        independent_variables_dict = {
            name: f"{value} {units}" if units else f"{value}"
            for name, (value, units) in constants_extracted_dict.items()
        }
        return independent_variables_dict
    independent_variables_dict = prepare_independent_variables(constants_extracted_dict)

    if graphical_dimensionality == 2:
        return independent_variables_dict, constants_extracted_dict, equation_extracted_dict, x_variable_extracted_dict, y_variable_extracted_dict
    if graphical_dimensionality == 3:
        return independent_variables_dict, constants_extracted_dict, equation_extracted_dict, x_variable_extracted_dict, y_variable_extracted_dict, z_variable_extracted_dict

# equation_dict = {
#     'equation_string': 'k = A*(e**((-Ea)/(R*T)))',
#     'x_variable': 'T (K)',  
#     'y_variable': 'k (s**(-1))',
#     'constants': {'Ea': '30000 (J)*(mol^(-1))', 'R': '8.314 (J)*(mol^(-1))*(K^(-1))' , 'A': '1E13 (s**-1)', 'e': '2.71828'},
#     'num_of_points': 10,
#     'x_range_default': [200, 500],
#     'x_range_limits' : [],
#     'points_spacing': 'Linear'
# }

# try:
#     result_extracted = parse_equation_dict(equation_dict)
#     print(result_extracted)
# except ValueError as e:
#     print(f"Error: {e}")


def generate_multiplicative_points(range_min, range_max, num_of_points=None, factor=None, reverse_scaling=False):
    """
    Generates a sequence of points using relative spacing within a normalized range,
    and spacing is based on a multiplicative factor (uniform when factor is 1).

    The function supports flexible spacing strategies, including equal intervals
    or multiplicative increments controlled via a scaling factor. It also supports
    reversed spacing (descending increment size), by instead applying
    the algorithm from from the upper bound down. The output always
    includes the exact values of `range_min` and `range_max`.

    Args:
        range_min (float): The lower bound of the range.
        range_max (float): The upper bound of the range.
        num_of_points (int, optional): Number of intermediate points to generate.
            Must be greater than 1 if provided.
        factor (float, optional): Multiplication factor used for exponential spacing.
            Must be greater than zero.
        reverse_scaling (bool, optional): If True, exponential scaling is applied
            in reverse, starting from `range_max` instead of `range_min`.

    Returns:
        list: A list of floating-point numbers representing the scaled positions
            within the specified range.

    Raises:
        ValueError: If both `num_of_points` and `factor` are not provided.

    Example:
        generate_multiplicative_points(0, 100, num_of_points=5)
        # Output: [0.0, 25.0, 50.0, 75.0, 100.0]

        generate_multiplicative_points(0, 100, factor=2)
        # Output: [0.0, 1.0, 3.0, 7.0, ..., 100.0] (approximate values based on spacing)
    """

    # Define normalized bounds
    relative_min = 0
    relative_max = 1
    total_value_range = range_max - range_min  

    # Case 1: num_of_points is provided (factor may be provided too)
    if num_of_points is not None and num_of_points > 1:
        
        # Case 1a: Generate points using equal spacing in relative space
        equal_spacing_list = [relative_min]  # Start at normalized min
        equal_spacing_value = (relative_max - relative_min) / (num_of_points - 1)  # Normalized step size

        for step_index in range(1, num_of_points):
            equal_spacing_list.append(relative_min + step_index * equal_spacing_value)

        # Case 1b: Generate points using multiplication factor (if provided)
        factor_spacing_list = [relative_min]
        if factor is not None and factor > 0:
            relative_spacing = 0.01  # Start at 1% of the range (normalized units)
            current_position = relative_min

            while current_position + relative_spacing < relative_max:
                current_position += relative_spacing
                factor_spacing_list.append(current_position)
                relative_spacing *= factor  # Multiply spacing by factor

        # Compare list lengths explicitly and select the better approach
        if len(factor_spacing_list) > len(equal_spacing_list):
            normalized_points = factor_spacing_list
        else:
            normalized_points = equal_spacing_list

    # Case 2: Only factor is provided, generate points using the multiplication factor
    elif factor is not None and factor > 0:
        relative_spacing = 0.01  # Start at 1% of the range
        current_position = relative_min
        normalized_points = [relative_min]

        while current_position + relative_spacing < relative_max:
            current_position += relative_spacing
            normalized_points.append(current_position)
            relative_spacing *= factor  # Multiply spacing by factor

    # Case 3: Neither num_of_points nor factor is provided, compute equal spacing dynamically
    elif num_of_points is None and factor is None:
        equal_spacing_value = (relative_max - relative_min) / 9  # Default to 9 intermediate points
        normalized_points = [relative_min + step_index * equal_spacing_value for step_index in range(1, 9)]

    # Case 4: Invalid input case—neither num_of_points nor factor is properly set
    else:
        raise ValueError("Either num_of_points or factor must be provided.")

    # Ensure the last relative point is relative_max before scaling
    if normalized_points[-1] != relative_max:
        normalized_points.append(relative_max)

    # Scale normalized points back to the actual range
    if reverse_scaling:
        scaled_points = [range_max - ((relative_max - p) * total_value_range) for p in normalized_points]  # Reverse scaling adjustment
    else:
        scaled_points = [range_min + (p * total_value_range) for p in normalized_points]

    return scaled_points

# # Example usages
# print("line 224")
# print(generate_multiplicative_points(0, 100, num_of_points=10, factor=2))  # Default exponential scaling from min end
# print(generate_multiplicative_points(0, 100, num_of_points=10, factor=2, reverse_scaling=True))  # Exponential scaling from max end
# print(generate_multiplicative_points(1, 100, num_of_points=10, factor=1.3)) # Compares num_of_points vs factor, chooses whichever makes more points
# print(generate_multiplicative_points(1, 100, num_of_points=10))            # Computes factor dynamically
# print(generate_multiplicative_points(1, 100, factor=2))                    # Uses factor normally
# print(generate_multiplicative_points(1, 100))                               # Uses step_factor for default 10 points with 8 intermediate values
# print("line 228")


# # Example usages with reverse scaling
# print("line 240")
# print(generate_multiplicative_points(-50, 100, num_of_points=10, factor=2))  # Case 1b: Uses spacing factor with num_of_points
# print(generate_multiplicative_points(-50, 100, num_of_points=10, factor=2, reverse_scaling=True))  # Reverse scaling version
# print(generate_multiplicative_points(-100, -10, num_of_points=5, factor=1.5)) # Case 1b: Works with negatives
# print(generate_multiplicative_points(-25, 75, num_of_points=7))               # Case 1a: Computes spacing dynamically
# print(generate_multiplicative_points(-10, 50, factor=1.3))                    # Case 2: Uses factor-based spacing
# print(generate_multiplicative_points(-30, 30))                                # Case 3: Uses default intermediate spacing

def generate_points_by_spacing(num_of_points=10, range_min=0, range_max=1, points_spacing="linear"):
    """
    Generates a sequence of numerical points using a selected spacing strategy across
    a defined range.

    Supports multiple spacing modes including uniform linear intervals, logarithmic
    steps, exponential growth, and multiplicative spacing using a user-specified factor.
    Automatically includes `range_min` and `range_max` in the returned list.

    Args:
        num_of_points (int): Number of values to generate within the range. Defaults to 10.
        range_min (float): Lower bound of the range. Defaults to 0.
        range_max (float): Upper bound of the range. Defaults to 1.
        points_spacing (str or float): Defines the spacing strategy. Accepted values:
            - "linear": Uniform spacing.
            - "logarithmic": Logarithmicly increasing values (which is exponential increase with base 10)
            - "exponential": Exponentially increasing values (exponential base e)
            - float > 0: Used as a multiplication factor for spacing (like doubling between points)

    Returns:
        list: A list of float values representing the computed points between the
            specified bounds.

    Raises:
        ValueError: If `points_spacing` is not supported or improperly defined.

    Example:
        generate_points_by_spacing(num_of_points=10, range_min=1, range_max=100, points_spacing="logarithmic")
        # Output: [1.0, 1.6681..., 2.7864..., ..., 100.0]
    """
    import numpy as np  # Ensure numpy is imported
    spacing_type = str(points_spacing).lower() if isinstance(points_spacing, str) else None
    points_list = None
    if num_of_points == None:
        num_of_points = 10
    if range_min == None:
        range_min = 0
    if range_max == None:
        range_max = 1
    if str(spacing_type).lower() == "none":
        spacing_type = "linear"
    if spacing_type == "":
        spacing_type = "linear"
    if spacing_type.lower() == "linear":
        points_list = np.linspace(range_min, range_max, num_of_points).tolist()
    elif spacing_type.lower() == "logarithmic":
        points_list = np.logspace(np.log10(range_min), np.log10(range_max), num_of_points).tolist()
    elif spacing_type.lower() == "exponential":
        points_list = (range_min * np.exp(np.linspace(0, np.log(range_max/range_min), num_of_points))).tolist()
    elif isinstance(points_spacing, (int, float)) and points_spacing > 0:
        points_list = generate_multiplicative_points(range_min, range_max, points_spacing, num_of_points)
    else:
        raise ValueError(f"Unsupported spacing type: {points_spacing}")

    return points_list


# # Example usage demonstrating different spacing types:
# print(generate_points_by_spacing(num_of_points=10, range_min=1, range_max=100, points_spacing="linear"))         # Linear spacing
# print(generate_points_by_spacing(num_of_points=10, range_min=1, range_max=100, points_spacing="logarithmic"))    # Logarithmic spacing
# print(generate_points_by_spacing(num_of_points=10, range_min=1, range_max=100, points_spacing="exponential"))    # Exponential spacing
# print(generate_points_by_spacing(num_of_points=10, range_min=1, range_max=100, points_spacing=2))               # Multiplicative factor spacing


def generate_points_from_range_dict(range_dict, variable_name="x"):
    """
    Generates a sequence of points for a specified variable using configuration
    values from a range_dict.

    This function extracts the relevant range and point-generation parameters based
    on naming conventions.

    The function follows these rules:
    1. If '{variable_name}_range_limits' is provided as a list of two numbers, it is used as the range.
    2. Otherwise, '{variable_name}_range_default' is used as the range.
    3. Calls generate_points_by_spacing() to generate the appropriate sequence based on num_of_points and points_spacing.
    
    It applies range narrowing if stricter limits are provided,
    and delegates the generation logic to `generate_points_by_spacing()` using the
    determined boundaries and settings.

    Args:
        range_dict (dict): A dictionary that may contain default range values,
            narrowed limits, and spacing configuration. Can include additional unused fields.
        variable_name (str, optional): The name of the variable used to construct
            lookup keys in range_dict (e.g., "x" → keys like "x_range_limits").
            Defaults to "x".

    Returns:
        list: A list of floats representing the generated sequence of points
            for the specified variable.

    Raises:
        ValueError: If neither default nor limit values specify a valid range.

    Example:
        range_dict = {
            "x_range_default": [0, 100],
            "x_range_limits": [10, 90],
            "num_of_points": 5,
            "points_spacing": "linear"
        }

        generate_points_from_range_dict(range_dict)
        # Output: [10.0, 30.0, 50.0, 70.0, 90.0]
    """
    range_default_key = f"{variable_name}_range_default"
    range_limits_key = f"{variable_name}_range_limits"

    # Assigning range. 
    # Start with default values
    if range_dict.get(range_default_key):  # get prevents crashing if the field is not present.
        range_min, range_max = range_dict[range_default_key]

    # If '{variable_name}_range_limits' is provided, update values only if they narrow the range
    if range_dict.get(range_limits_key):
        limit_min, limit_max = range_dict[range_limits_key]
        # Apply limits only if they tighten the range
        if limit_min is not None and limit_min > range_min:
            range_min = limit_min
        if limit_max is not None and limit_max < range_max:
            range_max = limit_max

    # Ensure at least one valid limit exists
    if range_min is None or range_max is None:
        raise ValueError(f"At least one min and one max must be specified between {variable_name}_range_default and {variable_name}_range_limits.")

    list_of_points = generate_points_by_spacing(
        num_of_points=range_dict['num_of_points'],
        range_min=range_min,
        range_max=range_max,
        points_spacing=range_dict['points_spacing']
    )
    # Generate points using the specified spacing method
    return list_of_points


## Start of Portion of code for parsing out tagged ustom units and returning them ##

def return_custom_units_markup(units_string, custom_units_list):
    """
    Wraps specified custom units in a string using angle brackets, with '<' and '>' so they are tagged.

    The function first sorts the custom unit list from longest to shortest to avoid
    premature replacement conflicts (e.g., 'meter' before 'm'). It then iterates
    through each unit and replaces its occurrences in the input string with a tagged
    version using angle brackets (e.g., "<meter>").

    Args:
        units_string (str): A string containing units or expressions with unit labels.
        custom_units_list (list): A list of custom unit strings to be wrapped in markup.

    Returns:
        str: A modified string with all matching custom unit names wrapped in '<>'.

    Example:
        units_string = "10 meter per second squared"
        custom_units_list = ["meter", "second"]
        return_custom_units_markup(units_string, custom_units_list)
        # Output: "10 <meter> per <second> squared"
    """
    sorted_custom_units_list = sorted(custom_units_list, key=len, reverse=True)
    #the units should be sorted from longest to shortest if not already sorted that way.
    for custom_unit in sorted_custom_units_list:
        units_string = units_string.replace(custom_unit, '<'+custom_unit+'>')
    return units_string

def extract_tagged_strings(text):
    """
    Extracts substrings enclosed in angle brackets (<>) from a text and returns
    them as a sorted list.

    Tags are typically used to mark custom units or identifiers within a string.
    Duplicate tags are removed, and the final list is sorted from longest to shortest
    to preserve priority in downstream replacements.

    Args:
        text (str): A string containing one or more tagged items formatted with angle
            brackets (e.g., "velocity in <meter_per_second> or <m/s>").

    Returns:
        list: A list of unique tagged strings sorted in descending order by length.

    Example:
        extract_tagged_strings("Speed: <meter_per_second>, Force: <newton>, Alt: <m>")
        # Output: ["meter_per_second", "newton", "m"]
    """
    list_of_tags = re.findall(r'<(.*?)>', text)
    set_of_tags = set(list_of_tags)
    sorted_tags = sorted(set_of_tags, key=len, reverse=True)
    return sorted_tags

##End of Portion of code for parsing out tagged ustom units and returning them ##



#This function is to convert things like (1/bar) to (bar)**(-1)
#It was written by copilot and refined by further prompting of copilot by testing.
#The depth is because the function works iteratively and then stops when finished.
def convert_inverse_units(expression, depth=100):
    """
    Converts reciprocal-style unit expressions into exponent notation for symbolic evaluation.

    Rewrites patterns such as "1/bar" into "(bar)**(-1)" and handles nested reciprocal
    cases through iterative pattern matching. The replacement process continues until
    no further changes are detected or a maximum iteration depth is reached.

    Args:
        expression (str): A string containing unit expressions with reciprocal notation
            (e.g., "1/bar", "1/(1/kg)").
        depth (int, optional): Maximum number of passes over the string to resolve nested
            reciprocals. Defaults to 100.

    Returns:
        str: The transformed expression with reciprocals converted to exponent form.

    Example:
        convert_inverse_units("1/bar")
        # Output: "(bar)**(-1)"

        convert_inverse_units("1/(1/kg)")
        # Output: "(kg)**(1)"
    """
    # Patterns to match valid reciprocals while ignoring multiplied units, so (1/bar)*bar should be  handled correctly.
    patterns = [r"1/\((1/.*?)\)", r"1/([a-zA-Z]+)"]
    for _ in range(depth):
        new_expression = expression
        for pattern in patterns:
            new_expression = re.sub(pattern, r"(\1)**(-1)", new_expression)
        
        # Stop early if no more changes are made
        if new_expression == expression:
            break
        expression = new_expression
    return expression

#It returnts two strings in a list, split at the first delimiter.
def split_at_first_delimiter(string, delimter=" "):
    """
    Splits a string into two parts at the first occurrence of a specified delimiter.

    This helper function is for parsing and separates a string
    based on the first occurrence of a chosen delimiter. If the delimiter is not found, the
    entire string is returned as the first element, with no second part.

    Args:
        string (str): The input string to be split.
        delimter (str, optional): The delimiter used to perform the split.
            Defaults to a single space (" ").

    Returns:
        list: A list containing two elements — the substring before the first
            delimiter, and the remainder of the string after it.

    Example:
        split_at_first_delimiter("unit kg", delimter=" ")
        # Output: ["unit", "kg"]

        split_at_first_delimiter("speed:30", delimter=":")
        # Output: ["speed", "30"]
    """
    return string.split(delimter, 1)

#This function takes an equation dict (see examples) and returns the x_points, y_points, and x_units and y_units.
#If there is more than one solution (like in a circle, for example) all solutions should be returned.
#The function is slow. I have checked what happens if "vectorize" is used on the x_point loop (which is the main work)
#and the function time didn't change. So the functions it calls must be where the slow portion is.
#I have not timed the individual functions to find and diagnose the slow step(s) to make them more efficient.
#Although there is lots of conversion between different object types to support the units format flexiblity that this function has,
#I would still expect the optimzed code to be an order of magnitude faster. So it may be worth finding the slow steps.
#One possibility might be to use "re.compile()"
def evaluate_equation_dict(equation_dict, verbose=False):
    """
    Evaluates a structured equation dictionary to compute output values across 
    dynamically generated input ranges, supporting both 2D and 3D data mappings.

    This function parses the input `equation_dict`, identifies independent and 
    dependent variables, and automatically detects and registers custom units. 
    It generates points along specified axes, solves the symbolic equation 
    for each set of inputs, and collects corresponding outputs. All custom units 
    are formatted and handled appropriately, including inverse notation and 
    tagged markup.

    Supports graphical dimensionality of 2 or 3:
    - For 2D, it computes y as a function of x.
    - For 3D, it computes z as a function of x and y.

    Args:
        equation_dict (dict): A dictionary containing:
            - equation_string (str): The symbolic equation to solve.
            - x_variable, y_variable, z_variable (str): Variable labels including units.
            - constants (dict): Named constants with units or plain values.
            - num_of_points (int): Number of evaluation points.
            - x_range_default, y_range_default (list): Default min/max ranges.
            - x_range_limits, y_range_limits (list): Optional bounds to narrow range.
            - x_points_specified (list): Currently unused.
            - points_spacing (str or float): Spacing for output points (linear, logarithmic, exponential, or factor).
            - reverse_scaling (bool): If True, spacing trend (such as exponential) is applied in reverse.
            - graphical_dimensionality (int, optional): Either 2 or 3. Defaults to 2 if unspecified.
            - verbose (bool, optional): Enables debug prints if True.

        verbose (bool, optional): If True, prints intermediate computation steps.

    Returns:
        dict: A dictionary containing:
            - graphical_dimensionality (int): Either 2 or 3.
            - x_units, y_units, z_units (str): Formatted and tagged unit strings.
            - x_points, y_points, z_points (list): Computed values from equation evaluation.

    Raises:
        ValueError: If graphical_dimensionality is not 2 or 3, or if valid range information is missing.

    Example:
        example_equation_dict = {
            'equation_string': 'k = A*(e**((-Ea)/(R*T)))',
            'x_variable': 'T (K)',
            'y_variable': 'k (s**(-1))',
            'constants': {
                'Ea': '30000 (J)*(mol^(-1))',
                'R': '8.314 (J)*(mol^(-1))*(K^(-1))',
                'A': '1*10^13 (s^-1)',
                'e': '2.71828'
            },
            'num_of_points': 10,
            'x_range_default': [200, 500],
            'points_spacing': 'Linear'
        }

        result = evaluate_equation_dict(example_equation_dict)
        # Returns a dictionary of computed x/y pairs and unit metadata
    """
    import copy
    equation_dict = copy.deepcopy(equation_dict)  # Create a deep copy to prevent unintended modifications
    #First a block of code to extract the x_points needed
    # Extract each dictionary key as a local variable
    equation_string = equation_dict['equation_string']
    if 'graphical_dimensionality' in equation_dict:
        graphical_dimensionality = equation_dict['graphical_dimensionality']
        graphical_dimensionality_added = False
    else: #assume graphical_dimensionality is 2 if one is not provided.
        equation_dict['graphical_dimensionality'] = 2
        graphical_dimensionality_added = True
        graphical_dimensionality = 2
    if 'verbose' in equation_dict:
        verbose = equation_dict["verbose"]
    # We don't need the below variables, because they are in the equation_dict.
    # x_variable = equation_dict['x_variable']
    # y_variable = equation_dict['y_variable']
    # constants = equation_dict['constants']
    # reverse_scaling = equation_dict['reverse_scaling']
    x_points = generate_points_from_range_dict(range_dict = equation_dict, variable_name='x')
    if graphical_dimensionality == 3: #for graphical_dimensionality of 3, the y_points are also an independent_variable to generate.
        y_points = generate_points_from_range_dict(range_dict = equation_dict, variable_name='y')

    #Now get the various variables etc.
    if graphical_dimensionality == 2:
        independent_variables_dict, constants_extracted_dict, equation_extracted_dict, x_variable_extracted_dict, y_variable_extracted_dict = parse_equation_dict(equation_dict=equation_dict)
        constants_extracted_dict, equation_extracted_dict #These will not be used. The rest of this comment is to avoid a vs code pylint flag. # pylint: disable=unused-variable, disable=pointless-statement
    elif graphical_dimensionality == 3:
        independent_variables_dict, constants_extracted_dict, equation_extracted_dict, x_variable_extracted_dict, y_variable_extracted_dict, z_variable_extracted_dict = parse_equation_dict(equation_dict=equation_dict)
        constants_extracted_dict, equation_extracted_dict #These will not be used. The rest of this comment is to avoid a vs code pylint flag. # pylint: disable=unused-variable, disable=pointless-statement
    else:
        raise ValueError("Error: graphical_dimensionality not received and/or not evaluatable by current code.")

    #Start of block to check for any custom units and add them to the ureg if necessary.
    custom_units_list = []
    #helper function to clean custom units brackets. In future, could be made more general rather than hardcoded as angle brackets.
    def clean_brackets(string):
        """
        Removes angle brackets from a string, typically used to strip markup from
        custom-tagged units or identifiers.

        This utility is useful for sanitizing strings that use '<>' as delimiters
        for tagging purposes. It preserves all other content while removing both
        opening and closing angle brackets.

        Args:
            string (str): The input string containing optional angle brackets.

        Returns:
            str: The cleaned string with all '<' and '>' characters removed.

        Example:
            clean_brackets("<meter_per_second>")
            # Output: "meter_per_second"
        """
        return string.replace("<", "").replace(">", "")

    for constant_entry_key in independent_variables_dict.keys():
        independent_variables_string = independent_variables_dict[constant_entry_key]
        custom_units_extracted = extract_tagged_strings(independent_variables_string)
        independent_variables_dict[constant_entry_key] = clean_brackets(independent_variables_dict[constant_entry_key])
        for custom_unit in custom_units_extracted: #this will be skipped if the list is empty.
            ureg.define(f"{custom_unit} = [custom]") #use "[custom]" to create a custom unit in the pint module.
        custom_units_list.extend(custom_units_extracted)
      
    #now also check for the x_variable_extracted_dict 
    custom_units_extracted = extract_tagged_strings(x_variable_extracted_dict["units"])
    x_variable_extracted_dict["units"] = clean_brackets(x_variable_extracted_dict["units"])
    for custom_unit in custom_units_extracted: #this will be skipped if the list is empty.
        ureg.define(f"{custom_unit} = [custom]") #use "[custom]" to create a custom unit in the pint module.
    custom_units_list.extend(custom_units_extracted)

    #now also check for the y_variable_extracted_dict (technically not needed)
    custom_units_extracted = extract_tagged_strings(y_variable_extracted_dict["units"])
    y_variable_extracted_dict["units"] = clean_brackets(y_variable_extracted_dict["units"])
    for custom_unit in custom_units_extracted: #this will be skipped if the list is empty.
        ureg.define(f"{custom_unit} = [custom]") #use "[custom]" to create a custom unit in the pint module.
    custom_units_list.extend(custom_units_extracted)

    if graphical_dimensionality == 3:
        #now also check for the z_variable_extracted_dict (technically not needed)
        custom_units_extracted = extract_tagged_strings(z_variable_extracted_dict["units"])
        z_variable_extracted_dict["units"] = clean_brackets(z_variable_extracted_dict["units"])
        for custom_unit in custom_units_extracted: #this will be skipped if the list is empty.
            ureg.define(f"{custom_unit} = [custom]") #use "[custom]" to create a custom unit in the pint module.
        custom_units_list.extend(custom_units_extracted)

    #now also check for the equation_string
    custom_units_extracted = extract_tagged_strings(equation_string)
    equation_string = clean_brackets(equation_string)
    for custom_unit in custom_units_extracted: #this will be skipped if the list is empty.
        ureg.define(f"{custom_unit} = [custom]") #use "[custom]" to create a custom unit in the pint module.
    custom_units_list.extend(custom_units_extracted)        
    
    # Remove duplicates by converting to a set and back to a list.
    custom_units_list = list(set(custom_units_list))
    #now sort from longest to shortest, since we will have to put them back in that way later.
    # Sort the unique units by length in descending order
    custom_units_list = sorted(custom_units_list, key=len, reverse=True)

    #End of block to check for any custom units and add them to the ureg if necessary.

    #For graphical_dimensionality of 2, The full list of independent variables includes the x_variable and the independent_variables. 
    independent_variables = list(independent_variables_dict.keys())#.append(x_variable_extracted_dict['label'])
    independent_variables.append(x_variable_extracted_dict['label'])
    if graphical_dimensionality == 3: #for graphical_dimensionality of 3, the y_variable is also an independent variable.
        independent_variables.append(y_variable_extracted_dict['label'])

    #Now define the dependent variable:
    if graphical_dimensionality == 2:
        dependent_variable = y_variable_extracted_dict["label"]
    elif graphical_dimensionality == 3:
        dependent_variable = z_variable_extracted_dict["label"]
    else:
        raise ValueError("Error: graphical_dimensionality not received and/or not evaluatable by current code.")
    solved_coordinates_list = [] #These are x,y pairs or x,y,z triplets. can't just keep y_points, because there could be more than one solution.
    y_units = ''#just initializing.
    dependent_variable_units = '' #just initializing.

    if graphical_dimensionality == 2:
        input_points_list = x_points #currently a list of points [1,2,3]
        #nested_x_points = [[x] for x in input_points_list] #this way could have  [ [x1],[x2],...]
    elif graphical_dimensionality == 3:
        import itertools
        input_points_list = list(itertools.product(x_points, y_points))  #[ [x1,y1], [x1,y2] ]        
    else:
        raise ValueError("Error: graphical_dimensionality not received and/or not evaluatable by current code.")

    for current_point in input_points_list:
        #For each point, need to call the "solve_equation" equation (or a vectorized version of it).
        #This is the form that the variables need to take
        # # Example usage
        # independent_variables_values_and_units = {
        #     "x": "2 m / s",
        #     "y": "3 meter"
        # }
        # We also need to define the independent variables and dependent variables.
        if graphical_dimensionality == 2:
            independent_variables_dict[x_variable_extracted_dict["label"]] = str(current_point) + " " + x_variable_extracted_dict["units"]
        if graphical_dimensionality == 3:
            independent_variables_dict[x_variable_extracted_dict["label"]] = str(current_point[0]) + " " + x_variable_extracted_dict["units"]
            independent_variables_dict[y_variable_extracted_dict["label"]] = str(current_point[1]) + " " + y_variable_extracted_dict["units"]
        #if graphical_dimensionality is 2D, dependent_variable_solutions is y_solutions. 
        #if graphical_dimensionality is 3D, dependent_variable_solutions is z_solutions. 
        if verbose: print("json_equationer > equation_evaluator > evaluate_equation_dict > current_point:", current_point)
        dependent_variable_solutions = solve_equation(equation_string, independent_variables_values_and_units=independent_variables_dict, dependent_variable=dependent_variable)
        if dependent_variable_solutions:
            for dependent_variable_point_with_units in dependent_variable_solutions:
                if graphical_dimensionality == 2:
                    y_point = float(dependent_variable_point_with_units.split(" ", 1)[0]) #the 1 splits only at first space.
                    solved_coordinates_list.append([current_point, y_point])
                    if dependent_variable_units == '': #only extract units the first time.
                        y_units = dependent_variable_point_with_units.split(" ", 1)[1] #the 1 splits only at first space.
                if graphical_dimensionality == 3:
                    z_point = float(dependent_variable_point_with_units.split(" ", 1)[0]) #the 1 splits only at first space.
                    solved_coordinates_list.append([current_point[0],current_point[1], z_point])
                    if dependent_variable_units == '': #only extract units the first time.
                        z_units = dependent_variable_point_with_units.split(" ", 1)[1] #the 1 splits only at first space.
                
    #now need to convert the x_y_pairs.
    # Separating x and y points
    if graphical_dimensionality == 2:
        x_points, y_points = zip(*solved_coordinates_list)
    elif graphical_dimensionality == 3:
        x_points, y_points, z_points = zip(*solved_coordinates_list)

    # Convert tuples to lists
    x_points = list(x_points)
    y_points = list(y_points)
    if graphical_dimensionality == 3:
        z_points = list(z_points)
  
    #Some lines to ensure units are appropriate format before doing any inverse units conversions.
    if graphical_dimensionality == 2:
        x_units = x_variable_extracted_dict["units"]
        if "(" not in x_units:
            x_units = "(" + x_units + ")"
        if "(" not in y_units:
            y_units = "(" + y_units + ")"

    if graphical_dimensionality == 3:
        x_units = x_variable_extracted_dict["units"]
        y_units = y_variable_extracted_dict["units"]
        if "(" not in x_units:
            x_units = "(" + x_units + ")"
        if "(" not in y_units:
            y_units = "(" + y_units + ")"
        if "(" not in z_units:
            z_units = "(" + z_units + ")"

    y_units = convert_inverse_units(y_units)
    x_units = convert_inverse_units(x_units)
    if graphical_dimensionality == 3:
        z_units = convert_inverse_units(z_units)

    #Put back any custom units tags, only needed for dependent variable.
    if graphical_dimensionality == 2:
        y_units = return_custom_units_markup(y_units, custom_units_list)
    if graphical_dimensionality == 3:
        z_units = return_custom_units_markup(z_units, custom_units_list)

    #Fill the dictionary that will be returned.
    evaluated_dict = {}
    evaluated_dict['graphical_dimensionality'] = graphical_dimensionality
    evaluated_dict['x_units'] = x_units
    evaluated_dict['y_units'] = y_units
    evaluated_dict['x_points'] = x_points
    evaluated_dict['y_points'] = y_points
    if graphical_dimensionality == 3:
        z_units = return_custom_units_markup(z_units, custom_units_list)
        evaluated_dict['z_units'] = z_units
        evaluated_dict['z_points'] = z_points
    if graphical_dimensionality_added == True: #undo adding graphical_dimensionality if it was added by this function.
        equation_dict.pop("graphical_dimensionality")
    return evaluated_dict

if __name__ == "__main__":
    #Here is a 2D example:
    example_equation_dict = {
        'equation_string': 'k = A*(e**((-Ea)/(R*T)))',
        'x_variable': 'T (K)',  
        'y_variable': 'k (s**(-1))',
        'constants': {'Ea': '30000 (J)*(mol^(-1))', 'R': '8.314 (J)*(mol^(-1))*(K^(-1))' , 'A': '1*10^13 (s^-1)', 'e': '2.71828'},
        'num_of_points': 10,
        'x_range_default': [200, 500],
        'x_range_limits' : [],
        'x_points_specified' : [],
        'points_spacing': 'Linear',
        'reverse_scaling' : False
    }

    example_evaluated_dict = evaluate_equation_dict(example_equation_dict)
    print(example_evaluated_dict)

    #Here is a 3D example.
    example_equation_dict = {
        'equation_string': 'k = A*(e**((-Ea)/(R*T)))',
        'graphical_dimensionality' : 3,
        'x_variable': 'T (K)',  
        'y_variable': 'Ea (J)*(mol^(-1))',
        'z_variable': 'k (s**(-1))', 
        'constants': {'R': '8.314 (J)*(mol^(-1))*(K^(-1))' , 'A': '1*10^13 (s^-1)', 'e': '2.71828'},
        'num_of_points': 10,
        'x_range_default': [200, 500],
        'x_range_limits' : [],
        'y_range_default': [30000, 50000],
        'y_range_limits' : [],
        'x_points_specified' : [],
        'points_spacing': 'Linear',
        'reverse_scaling' : False
    }

    example_evaluated_dict = evaluate_equation_dict(example_equation_dict)
    print(example_evaluated_dict)
