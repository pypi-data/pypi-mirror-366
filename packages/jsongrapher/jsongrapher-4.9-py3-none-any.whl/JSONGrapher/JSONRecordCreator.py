import json
import JSONGrapher.styles.layout_styles_library
import JSONGrapher.styles.trace_styles_collection_library
import JSONGrapher.version
#TODO: put an option to suppress warnings from JSONRecordCreator


#Start of the portion of the code for the GUI##
global_records_list = [] #This list holds onto records as they are added. Index 0 is the merged record. Each other index corresponds to record number (like 1 is first record, 2 is second record, etc)



#This is a JSONGrapher specific function
#That takes filenames and adds new JSONGrapher records to a global_records_list
#If the all_selected_file_paths and newest_file_name_and_path are [] and [], that means to clear the global_records_list.
def add_records_to_global_records_list_and_plot(all_selected_file_paths, newly_added_file_paths, plot_immediately=True):
    """
    Typically adds new JSONGrapher records to a global records list, merging their data into the main record, and also launches the new plot.
    
    In the desktop/local version of JSONgrapehr, a global variable with a records list is used to keep track of JSONGrapher records added
    As this is the desktop/local version of JSONGrapher, the inputs to this function are actually file paths,
    and those file paths are used to create JSONGrapher record objects.
    This function takes in the existing file paths of records in the global records list as well as any newly added file paths.
    The function does not take the global records list as an argument but treats it as an implicit argument.
    As records are added, they are stored in thes global records list before being merged.

    If both input path lists for this function are empty, the global records list is cleared.
    If input paths are received, if no prior records exist, a new record is created and used as the merge base. Otherwise, new records are appended and merged
    into the existing master record. Optionally triggers a plot update and returns a JSON string
    representation of the updated figure.

    Args:
        all_selected_file_paths (list[str]): All file paths currently selected by the user.
        newly_added_file_paths (list[str]): File paths recently added to the selection.
        plot_immediately (bool, optional): Whether to trigger a plot update after processing. Default is True.

    Returns:
        list[str]: A list containing a JSON string of the updated figure, suitable for export.
    """
    #First check if we have received a "clear" condition.
    if (len(all_selected_file_paths) == 0) and (len(newly_added_file_paths) == 0):
        global_records_list.clear()
        return global_records_list
    if len(global_records_list) == 0: #this is for the "first time" the function is called, but the newly_added_file_paths could be a list longer than one.
        first_record = create_new_JSONGrapherRecord()
        first_record.import_from_file(newly_added_file_paths[0]) #get first newly added record record.
        #index 0 will be the one we merge into.
        global_records_list.append(first_record)
        #index 1 will be where we store the first record, so we append again.
        global_records_list.append(first_record)
        #Now, check if there are more records.
        if len(newly_added_file_paths) > 1:
            for filename_and_path_index, filename_and_path in enumerate(newly_added_file_paths):
                if filename_and_path_index == 0:
                    pass #passing because we've already added first file.
                else:
                    current_record = create_new_JSONGrapherRecord() #make a new record
                    current_record.import_from_file(filename_and_path)        
                    global_records_list.append(current_record) #append it to global records list
                    global_records_list[0] = merge_JSONGrapherRecords([global_records_list[0], current_record]) #merge into the main record of records list, which is at index 0.
    else: #For case that global_records_list already exists when funciton is called.
        for filename_and_path_index, filename_and_path in enumerate(newly_added_file_paths):
            current_record = create_new_JSONGrapherRecord() #make a new record
            current_record.import_from_file(filename_and_path)        
            global_records_list.append(current_record) #append it to global records list
            global_records_list[0] = merge_JSONGrapherRecords([global_records_list[0], current_record]) #merge into the main record of records list, which is at index 0.
    if plot_immediately:
        #plot the index 0, which is the most up to date merged record.
        global_records_list[0].plot_with_plotly()
    json_string_for_download = json.dumps(global_records_list[0].fig_dict, indent=4)
    return [json_string_for_download] #For the GUI, this function should return a list with something convertable to string to save to file, in index 0.



#This ia JSONGrapher specific wrapper function to drag_and_drop_gui create_and_launch.
#This launches the python based JSONGrapher GUI.
def launch():
    """
    Launches the JSONGrapher graphical user interface.

    Attempts to import and start the drag-and-drop GUI interface used for selecting files
    and triggering the record addition workflow. 
    In the desktop/local version of JSONGrapher, the a global variable is used
    to store each record as is added and merged in.
    This function returns that updated global records list.
    The first index of the global records list will include the merged record.

    Args:
        No arguments.
        
    Returns:
        list[JSONGrapherRecord]: The updated list of global records after GUI interaction.
    """
    try:
        import JSONGrapher.drag_and_drop_gui as drag_and_drop_gui
    except ImportError:
        try:
            import drag_and_drop_gui  # Attempt local import
        except ImportError as exc:
            raise ImportError("Module 'drag_and_drop_gui' could not be found locally or in JSONGrapher.") from exc
    _selected_files = drag_and_drop_gui.create_and_launch(app_name = "JSONGrapher", function_for_after_file_addition=add_records_to_global_records_list_and_plot)
    #We will not return the _selected_files, and instead will return the global_records_list.
    return global_records_list

## End of the portion of the code for the GUI##


#the function create_new_JSONGrapherRecord is intended to be "like" a wrapper function for people who find it more
# intuitive to create class objects that way, this variable is actually just a reference
# so that we don't have to map the arguments.
def create_new_JSONGrapherRecord(hints=False):
    """
    Creates and returns a new JSONGrapherRecord instance, representing a JSONGrapher record.

    Constructs the new record using the JSONGrapherRecord class constructor. If hints are enabled,
    additional annotation fields are pre-populated to guide user input.

    Args:
        hints (bool, optional): Whether to include hint fields in the new record. Defaults to False.

    Returns:
        JSONGrapherRecord: A new instance of a JSONGrapher record, optionally populated with hints.
    """
    #we will create a new record. While we could populate it with the init,
    #we will use the functions since it makes thsi function a bit easier to follow.
    new_record = JSONGrapherRecord()
    if hints == True:
        new_record.add_hints()
    return new_record

#This is actually a wrapper around merge_JSONGrapherRecords. Made for convenience.
def load_JSONGrapherRecords(recordsList):
    """
    This is actually a wrapper around merge_JSONGrapherRecords. Made for convenience.
    Merges a list of JSONGrapher records into a single combined record.

    Passes the provided list directly into the merge function, which consolidates
    multiple records into a single, unified structure.

    Args:
        recordsList (list[JSONGrapherRecord]): A list of JSONGrapher records to merge.

    Returns:
        JSONGrapherRecord: A single merged record resulting from merging all input records.
    """
    return merge_JSONGrapherRecords(recordsList)

#This is actually a wrapper around merge_JSONGrapherRecords. Made for convenience.
def import_JSONGrapherRecords(recordsList):
    """
    This is actually a wrapper around merge_JSONGrapherRecords. Made for convenience.
    Imports and merges multiple JSONGrapher records into a single consolidated record.
    
    This works because when merge_JSONGrapherRecords receives a list
    it checks whether each item in the list is a filepath or a record,
    and when it is a filepath the merge_JSONGrapherRecords function
    will automatically import the record from the filepath to make a new record.

    This function delegates directly to the merge function to unify all records in the provided list.

    Args:
        recordsList (list[JSONGrapherRecord]): The list of records to merge.

    Returns:
        JSONGrapherRecord: A single merged record resulting from merging all input records.
    """
    return merge_JSONGrapherRecords(recordsList)

#This is a function for merging JSONGrapher records.
#recordsList is a list of records 
#Each record can be a JSONGrapherRecord object (a python class object) or a dictionary (meaning, a JSONGrapher JSON as a dictionary)
#If a record is received that is a string, then the function will attempt to convert that into a dictionary.
#The units used will be that of the first record encountered
#if changing this function's arguments, then also change those for load_JSONGrapherRecords and import_JSONGrapherRecords
def merge_JSONGrapherRecords(recordsList):
    """
    Merges multiple JSONGrapher records into one, including converting units by scaling data as needed.

    Accepts a list of records, each of which may be a JSONGrapherRecord instance, JSONGrapher records as dictionaries 
    (which are basically JSON objects), or a string which is filepath to a stored JSON file.
    The records list received can be a mix between these different types of ways of providing reords.
    
    For each record, the figure dictionary (fig_dict) is extracted and used for merging. Unit labels are compared and,
    if necessary, data values are scaled to match the units of the first record before merging.
    All data series are consolidated into the single single merged record that is returned.

    Args:
        recordsList (list): A list of records to merge. May include JSONGrapherRecord instances, JSONGrapher records as dictionaries 
    (which are basically JSON objects), or a string which is filepath to a stored JSON file.

    Returns:
        JSONGrapherRecord: A single merged record resulting from merging all input records.
    """
    if type(recordsList) == type(""):
        recordsList = [recordsList]
    import copy
    recordsAsDictionariesList = []
    merged_JSONGrapherRecord = create_new_JSONGrapherRecord()
    #first make a list of all the records as dictionaries.
    for record in recordsList:
        if isinstance(record, dict):#can't use type({}) or SyncedDict won't be included.
            recordsAsDictionariesList.append(record)
        elif type(record) == type("string"):
            new_record = create_new_JSONGrapherRecord()
            new_fig_dict = new_record.import_from_json(record)
            recordsAsDictionariesList.append(new_fig_dict)
        else: #this assumpes there is a JSONGrapherRecord type received. 
            record = record.fig_dict
            recordsAsDictionariesList.append(record)
    #next, iterate through the list of dictionaries and merge each data object together.
    #We'll use the the units of the first dictionary.
    #We'll put the first record in directly, keeping the units etc. Then will "merge" in the additional data sets.
    #Iterate across all records received.
    for dictionary_index, current_fig_dict in enumerate(recordsAsDictionariesList):
        if dictionary_index == 0: #this is the first record case. We'll use this to start the list and also gather the units.
            merged_JSONGrapherRecord.fig_dict = copy.deepcopy(recordsAsDictionariesList[0])
            first_record_x_label = recordsAsDictionariesList[0]["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
            first_record_y_label = recordsAsDictionariesList[0]["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
            first_record_x_units = separate_label_text_from_units(first_record_x_label)["units"]
            first_record_y_units = separate_label_text_from_units(first_record_y_label)["units"]
        else:
            #first get the units of this particular record.
            this_record_x_label = recordsAsDictionariesList[dictionary_index]["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
            this_record_y_label = recordsAsDictionariesList[dictionary_index]["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
            this_record_x_units = separate_label_text_from_units(this_record_x_label)["units"]
            this_record_y_units = separate_label_text_from_units(this_record_y_label)["units"]
            #now get the ratio of the units for this record relative to the first record.
            #if the units are identical, then just make the ratio 1.
            if this_record_x_units == first_record_x_units:
                x_units_ratio = 1
            else:
                x_units_ratio = get_units_scaling_ratio(this_record_x_units, first_record_x_units)
            if this_record_y_units == first_record_y_units:
                y_units_ratio = 1
            else:
                y_units_ratio = get_units_scaling_ratio(this_record_y_units, first_record_y_units)
            #A record could have more than one data series, but they will all have the same units.
            #Thus, we use a function that will scale all of the dataseries at one time.
            if (x_units_ratio == 1) and (y_units_ratio == 1): #skip scaling if it's not necessary.
                scaled_fig_dict = current_fig_dict
            else:
                scaled_fig_dict = scale_fig_dict_values(current_fig_dict, x_units_ratio, y_units_ratio)
            #now, add the scaled data objects to the original one.
            #This is fairly easy using a list extend.
            merged_JSONGrapherRecord.fig_dict["data"].extend(scaled_fig_dict["data"])
    merged_JSONGrapherRecord = convert_JSONGRapherRecord_data_list_to_class_objects(merged_JSONGrapherRecord)
    return merged_JSONGrapherRecord

def convert_JSONGRapherRecord_data_list_to_class_objects(record):
    """
    Converts the list of data series objects in the 'data' field of a JSONGrapher record into a list of JSONGrapherDataSeries objects.

    Each data series object is typically a dictionary,
    The function essentially casts dictionaries into JSONGrapherDataSeries objects.

    Accepts either a JSONGrapherRecord or a standalone figure dictionary. Each entry in the
    list of the 'data' field is replaced with a JSONGrapherDataSeries instance,
    preserving any existing fields in each data series dictionary. The transformed record or fig_dict is returned.

    Args:
        record ( JSONGrapherRecord | dict ): A record or figure dictionary to transform.

    Returns:
        JSONGrapherRecord | dict: The updated record or dictionary with casted data series objects.
    """
    #will also support receiving a fig_dict
    if isinstance(record, dict):
        fig_dict_received = True
        fig_dict = record
    else:
        fig_dict_received = False
        fig_dict = record.fig_dict
    data_list = fig_dict["data"]
    #Do the casting into data_series objects by creating a fresh JSONDataSeries object and populating it.
    for data_series_index, data_series_received in enumerate(data_list):
        JSONGrapher_data_series_object = JSONGrapherDataSeries()
        JSONGrapher_data_series_object.update_while_preserving_old_terms(data_series_received)
        data_list[data_series_index] = JSONGrapher_data_series_object
    #Now prepare for return.
    if fig_dict_received == True:
        fig_dict["data"] = data_list
        record = fig_dict
    if fig_dict_received == False:
        record.fig_dict["data"] = data_list
    return record

### Start of portion of the file that has functions for scaling data to the same units ###
#The below function takes two units strings, such as
#    "(((kg)/m))/s" and  "(((g)/m))/s"
# and then returns the scaling ratio of units_string_1 / units_string_2
# So in the above example, would return 1000.
#Could add "tag_characters"='<>' as an optional argument to this and other functions
#to make the option of other characters for custom units.
def get_units_scaling_ratio(units_string_1, units_string_2):
    """
    Calculate the scaling ratio between two unit strings, returns ratio from units_string_1 / units_string_2.
    Unit strings may include parentheses, division symbols, multiplication symbols, and exponents.
    

    This function computes the multiplicative ratio required to convert from
    `units_string_1` to `units_string_2`. For example, converting from "(((kg)/m))/s" to "(((g)/m))/s"
    yields a scaling ratio of 1000.

    Unit expressions may include custom units if they are tagged in advance with angle brackets
    like "<umbrella>/m^(-2)".

    The function uses the `unitpy` library for parsing and unit arithmetic. 

    Reciprocal units with a "1" can cause issues (e.g., "1/bar"), the
    function attempts a fallback conversion in those cases.
    It is recommended to instead use exponents like "bar^(-1)"

    Args:
    units_string_1 (str): The source units as a string expression.
    units_string_2 (str): The target units as a string expression.

    Returns:
    float: The numerical ratio to convert values in `units_string_1`
    to `units_string_2`.

    Raises:
    KeyError: If a required unit is missing from the definition registry.
    ValueError: If the unit format is invalid or conversion fails.
    RuntimeError: For any unexpected errors during conversion.
    """
    # Ensure both strings are properly encoded in UTF-8
    units_string_1 = units_string_1.encode("utf-8").decode("utf-8")
    units_string_2 = units_string_2.encode("utf-8").decode("utf-8")
    #If the unit strings are identical, there is no need to go further.
    if units_string_1 == units_string_2:
        return 1
    import unitpy #this function uses unitpy.
    #for the purposes of this function, there are some unit strings which we will replace.
    dictionary_for_replacements = {"electron_volt":"eV"}
    keys_list = list(dictionary_for_replacements.keys())
    for key in keys_list:
        units_string_1 = units_string_1.replace(key, dictionary_for_replacements[key])
        units_string_2 = units_string_2.replace(key, dictionary_for_replacements[key])
    #Replace "^" with "**" for unit conversion purposes.
    #We won't need to replace back because this function only returns the ratio in the end.
    units_string_1 = units_string_1.replace("^", "**")
    units_string_2 = units_string_2.replace("^", "**")
    #For now, we need to tag µ symbol units as if they are custom units. Because unitpy doesn't support that symbol yet (May 2025)
    units_string_1 = tag_micro_units(units_string_1)
    units_string_2 = tag_micro_units(units_string_2)
    #Next, need to extract custom units and add them to unitpy
    custom_units_1 = extract_tagged_strings(units_string_1)
    custom_units_2 = extract_tagged_strings(units_string_2)
    for custom_unit in custom_units_1:
        add_custom_unit_to_unitpy(custom_unit)
    for custom_unit in custom_units_2:
        add_custom_unit_to_unitpy(custom_unit)
    #Now, remove the "<" and ">" and will put them back later if needed.
    units_string_1 = units_string_1.replace('<','').replace('>','')
    units_string_2 = units_string_2.replace('<','').replace('>','')
    try:
        #First need to make unitpy "U" object and multiply it by 1. 
        #While it may be possible to find a way using the "Q" objects directly, this is the way I found so far, which converts the U object into a Q object.
        units_object_converted = 1*unitpy.U(units_string_1)
        ratio_with_units_object = units_object_converted.to(units_string_2)
    #the above can fail if there are reciprocal units like 1/bar rather than (bar)**(-1), so we have an except statement that tries "that" fix if there is a failure.
    except Exception as general_exception: # This is so VS code pylint does not flag this line. pylint: disable=broad-except, disable=unused-variable
        units_string_1 = convert_inverse_units(units_string_1)
        units_string_2 = convert_inverse_units(units_string_2)
        units_object_converted = 1*unitpy.U(units_string_1)
        try:
            ratio_with_units_object = units_object_converted.to(units_string_2)
        except KeyError as e: 
            raise KeyError(f"Error during unit conversion in get_units_scaling_ratio: Missing key {e}. Ensure all unit definitions are correctly set. Unit 1: {units_string_1}, Unit 2: {units_string_2}") from e
        except ValueError as e:
            raise ValueError(f"Error during unit conversion in get_units_scaling_ratio: {e}. Make sure unit values are valid and properly formatted. Unit 1: {units_string_1}, Unit 2: {units_string_2}") from e       
        except Exception as e:  # pylint: disable=broad-except
            raise RuntimeError(f"An unexpected error occurred in get_units_scaling_ratio when trying to convert units: {e}. Double-check that your records have the same units. Unit 1: {units_string_1}, Unit 2: {units_string_2}") from e

    ratio_with_units_string = str(ratio_with_units_object)

    ratio_only = ratio_with_units_string.split(' ')[0] #what comes out may look like 1000 gram/(meter second), so we split and take first part.
    ratio_only = float(ratio_only)
    return ratio_only #function returns ratio only. If function is later changed to return more, then units_strings may need further replacements.

def return_custom_units_markup(units_string, custom_units_list):
    """
    Puts markup around custom units with '<' and '>'.
    
    This function receives a units_string and a custom_units_list which is a list of strings
    and then puts tagging markup on any custom units within the units_string, 'tagging' them with '<' and '>'
    The units_string may include *, /, ^, and ( ).
        
    For example, if the units string was "((umbrella)/m^(-2))" 
    And the custom_units_list was ['umbrella'],
    the string returned would be "((<umbrella>)/m^(-2))" 
    If the custom_units_list is empty or custom units are not found
    then no change is made to the units string.

    Args:
        units_string (str): The input string that may contain units (e.g., "10kohm").
        custom_units_list (List[str]): A list of custom unit strings to search for 
            and wrap in markup.

    Returns:
        str: The updated string with custom units wrapped in angle brackets (e.g., "((umbrella)/m^(-2))" ).
    """
    
    sorted_custom_units_list = sorted(custom_units_list, key=len, reverse=True)
    #the units should be sorted from longest to shortest if not already sorted that way.
    for custom_unit in sorted_custom_units_list:
        units_string = units_string.replace(custom_unit, '<'+custom_unit+'>')
    return units_string

    #This function tags microunits.
    #However, because unitpy gives unexpected behavior with the microsymbol,
    #We are actually going to change them from "µm" to "<microfrogm>"
def tag_micro_units(units_string):
    """
    Replaces micro symbol-prefixed units with a custom tagged format for internal use.

    This function scans a unit string for various Unicode representations of the micro symbol 
    (e.g., "µ", "μ", "𝜇", "𝝁") followed by standard unit characters, such as "μm".
    
    It replaces each match with a placeholder tag that converts the micro symbol
    to the word "microfrog" with pattern "<microfrogX>", such as "μm*s^(-1)" → "<microfrogm>*s^(-1)"
    
    The reason to replace the micro symbols is to avoid any incompatibilities with 
    functions or packages that would handle the micro symbols incorrectly,
    especially because there are multiple micro symbols. The reason that "microfrog" is used is 
    because it is distinct enough for us to convert back to microsymbol later.

    Args:
        units_string (str): A units string potentially containing µ symbols as prefixes, such as "μm*s^(-1)".

    Returns:
        str: A modified string with units containing micro symbols replaced by custom units tags containing "microfrog", such as "<microfrogm>*s^(-1)"
    """
    # Unicode representations of micro symbols:
    # U+00B5 → µ (Micro Sign)
    # U+03BC → μ (Greek Small Letter Mu)
    # U+1D6C2 → 𝜇 (Mathematical Greek Small Letter Mu)
    # U+1D6C1 → 𝝁 (Mathematical Bold Greek Small Letter Mu)
    micro_symbols = ["µ", "μ", "𝜇", "𝝁"]
    # Check if any micro symbol is in the string
    if not any(symbol in units_string for symbol in micro_symbols):
        return units_string  # If none are found, return the original string unchanged
    import re
    # Construct a regex pattern to detect any micro symbol followed by letters
    pattern = r"[" + "".join(micro_symbols) + r"][a-zA-Z]+"
    # Extract matches and sort them by length (longest first)
    matches = sorted(re.findall(pattern, units_string), key=len, reverse=True)
    # Replace matches with custom unit notation <X>
    for match in matches:
        frogified_match = f"<microfrog{match[1:]}>"
        units_string = units_string.replace(match, frogified_match)
    return units_string

    #We are actually going to change them back to "µm" from "<microfrogm>"
def untag_micro_units(units_string):
    """
    Restores standard micro-prefixed units from internal "microfrog" tagged format.

    This function reverses the transformation applied by `tag_micro_units`, converting 
    placeholder tags like "<microfrogF>" back into units with the Greek micro symbol 
    (such as, "μF"). This simply returns to having micro symbols in unit strings for display
    and for record exporting, once the algorithmic work is done.
    For example, from "<microfrogm>*s^(-1)" to "μm*s^(-1)".

    Note that we always use µ which is unicode U+00B5 adnd this may be different
    from the original micro symbol before the algorithm started.
    See tag_micro_units function comments for more information about microsymbols.

    Args:
        units_string (str): A string potentially containing tagged micro-units, like "<microfrogm>*s^(-1)"

    Returns:
        str: The string with tags converted back to standard micro-unit notation (such as from "<microfrogm>*s^(-1)" to "μm*s^(-1)" ).
    """
    if "<microfrog" not in units_string:  # Check if any frogified unit exists
        return units_string
    import re
    # Pattern to detect the frogified micro-units
    pattern = r"<microfrog([a-zA-Z]+)>"
    # Replace frogified units with µ + the original unit suffix
    return re.sub(pattern, r"µ\1", units_string)

def add_custom_unit_to_unitpy(unit_string):
    """
    Registers a new custom unit in the UnitPy framework for internal use.

    This function adds a user-defined unit to the UnitPy system by inserting a BaseUnit 
    into the global base dictionary and defining an Entry using a BaseSet. It's designed 
    to expand UnitPy's supported units dynamically while preventing duplicate entries 
    that could cause runtime issues.

    Args:
        unit_string (str): The name of the unit to register (such as, "umbrellaArea").
    """
    import unitpy
    from unitpy.definitions.entry import Entry
    #need to put an entry into "bases" because the BaseSet class will pull from that dictionary.
    unitpy.definitions.unit_base.bases[unit_string] = unitpy.definitions.unit_base.BaseUnit(label=unit_string, abbr=unit_string,dimension=unitpy.definitions.dimensions.dimensions["amount_of_substance"])
    #Then need to make a BaseSet object to put in. Confusingly, we *do not* put a BaseUnit object into the base_unit argument, below. 
    #We use "mole" to avoid conflicting with any other existing units.
    base_unit =unitpy.definitions.unit_base.BaseSet(mole = 1)
    #base_unit = unitpy.definitions.unit_base.BaseUnit(label=unit_string, abbr=unit_string,dimension=unitpy.definitions.dimensions.dimensions["amount_of_substance"])
    new_entry = Entry(label = unit_string, abbr = unit_string, base_unit = base_unit, multiplier= 1)
    #only add the entry if it is missing. A duplicate entry would cause crashing later.
    #We can't use the "unitpy.ledger.get_entry" function because the entries have custom == comparisons
    # and for the new entry, it will also return a special NoneType that we can't easy check.
    # the structer unitpy.ledger.units is a list, but unitpy.ledger._lookup is a dictionary we can use
    # to check if the key for the new unit is added or not.
    if unit_string not in unitpy.ledger._lookup:  #This comment is so the VS code pylint does not flag this line. pylint: disable=protected-access
        unitpy.ledger.add_unit(new_entry) #implied return is here. No return needed.

def extract_tagged_strings(text):
    """
    Extracts and returns a sorted list of unique substrings found within angle brackets.

    This function identifies all substrings wrapped in angle brackets (such as "<umbrella>"), 
    removes duplicates, and returns them sorted by length in descending order. It's useful 
    for parsing tagged text where the tags follow a consistent markup format.

    Args:
        text (str): A string potentially containing angle-bracketed tags.

    Returns:
        List[str]: A list of unique tags sorted from longest to shortest.
    """
    """Extracts tags surrounded by <> from a given string. Used for custom units.
       returns them as a list sorted from longest to shortest"""
    import re
    list_of_tags = re.findall(r'<(.*?)>', text)
    set_of_tags = set(list_of_tags)
    sorted_tags = sorted(set_of_tags, key=len, reverse=True)
    return sorted_tags

#This function is to convert things like (1/bar) to (bar)**(-1)
#It was written by copilot and refined by further prompting of copilot by testing.
#The depth is because the function works iteratively and then stops when finished.
def convert_inverse_units(expression, depth=100):
    """
    Converts unit reciprocals in string expressions to exponent notation.

    This function detects reciprocal expressions like "1/m" or nested forms such as 
    "1/(1/m)" and converts them into exponent format (such as "m**(-1)"). It processes 
    the expression iteratively up to the specified depth to ensure all nested reciprocals 
    are resolved. This helps standardize units for parsing or evaluation.

    Args:
        expression (str): A string containing unit expressions to transform.
        depth (int, optional): Maximum number of recursive replacements. Default is 100.

    Returns:
        str: A string with all convertible reciprocal units expressed using exponents.
    """
    import re
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

#the below function takes in a fig_dict, as well as x and/or y scaling values.
#The function then scales the values in the data of the fig_dict and returns the scaled fig_dict.
def scale_fig_dict_values(fig_dict, num_to_scale_x_values_by = 1, num_to_scale_y_values_by = 1):
    """
    Scales the 'x' and/or 'y' values in a figure dictionary for rescaling plotted data.

    This function takes a figure dictionary from JSONGrapher which has the same structure
    as a Plotly figure dictionary, deep-copies it, and applies x/y scaling factors to each data 
    series using the helper function `scale_dataseries_dict`.

    Args:
        fig_dict (dict): A dictionary containing figure data with a "data" key.
        num_to_scale_x_values_by (float, optional): Factor to scale all x-values. Defaults to 1.
        num_to_scale_y_values_by (float, optional): Factor to scale all y-values. Defaults to 1.

    Returns:
        dict: A new figure dictionary with scaled x and/or y data values.
    """
    import copy
    scaled_fig_dict = copy.deepcopy(fig_dict)
    #iterate across the data objects inside, and change them.
    for data_index, dataseries in enumerate(scaled_fig_dict["data"]):
        dataseries = scale_dataseries_dict(dataseries, num_to_scale_x_values_by=num_to_scale_x_values_by, num_to_scale_y_values_by=num_to_scale_y_values_by)
        scaled_fig_dict["data"][data_index] = dataseries #this line shouldn't be needed due to mutable references, but adding for clarity and to be safe.
    return scaled_fig_dict


def scale_dataseries_dict(dataseries_dict, num_to_scale_x_values_by = 1, num_to_scale_y_values_by = 1, num_to_scale_z_values_by = 1):
    """
    Applies scaling factors to x, y, and optionally z data in a data series dictionary.

    This function updates the numeric values in a data series dictionary by applying 
    scaling factors to each axis. It supports scaling for 2D and 3D datasets, and ensures 
    that all resulting values are converted to standard Python floats for compatibility 
    and serialization.

    Args:
        dataseries_dict (dict): A dictionary with keys "x", "y", and optionally "z", 
            each mapping to a list of numeric values.
        num_to_scale_x_values_by (float, optional): Factor by which to scale x-values. Default is 1.
        num_to_scale_y_values_by (float, optional): Factor by which to scale y-values. Default is 1.
        num_to_scale_z_values_by (float, optional): Factor by which to scale z-values (if present). Default is 1.

    Returns:
        dict: The updated data series dictionary with scaled numeric values.
    """
    import numpy as np
    dataseries = dataseries_dict
    dataseries["x"] = list(np.array(dataseries["x"], dtype=float)*num_to_scale_x_values_by) #convert to numpy array for multiplication, then back to list.
    dataseries["y"] = list(np.array(dataseries["y"], dtype=float)*num_to_scale_y_values_by) #convert to numpy array for multiplication, then back to list.
    
    # Ensure elements are converted to standard Python types. 
    dataseries["x"] = [float(val) for val in dataseries["x"]] #This line written by copilot.
    dataseries["y"] = [float(val) for val in dataseries["y"]] #This line written by copilot.

    if "z" in dataseries:
        dataseries["z"] = list(np.array(dataseries["z"], dtype=float)*num_to_scale_z_values_by) #convert to numpy array for multiplication, then back to list.
        dataseries["z"] = [float(val) for val in dataseries["z"]] #Mimicking above lines.
    return dataseries_dict

### End of portion of the file that has functions for scaling data to the same units ###

## This is a special dictionary class that will allow a dictionary
## inside a main class object to be synchronized with the fields within it.
class SyncedDict(dict):
    """Enables an owner object that is not a dictionary to behave like a dictionary.
    Each SyncedDict instance is a dictionary that automatically updates and synchronizes attributes with the owner object."""
    def __init__(self, owner):
        """
        Initialize a SyncedDict with an associated owner, where the fields of the owner will be synchronized.

        This constructor sets up the base dictionary and stores a reference to the owner
        object whose attributes should remain in sync with the dictionary entries.
        This allows a non-dictionary class object (the owner) to behave like a dictionary.

        Args:
            owner (object): The parent object that holds this dictionary and will mirror its keys as attributes.

        Returns:
            None
            
        """

        super().__init__()
        self.owner = owner  # Store reference to the class instance
    def __setitem__(self, key, value):
        """
        Set a key-value pair in the dictionary and update the owner's attribute.

        Ensures that when a new item is added or updated in the dictionary, the corresponding
        attribute on the owner object reflects the same value.

        Args:
            key (str): The key to assign.
            value (any): The value to assign to the key and the owner's attribute.

        Returns:
            None
            

        """

        super().__setitem__(key, value)  # Set in the dictionary
        setattr(self.owner, key, value)  # Sync with instance attribute
    def __delitem__(self, key):
        """
        Delete a key from the dictionary and remove its attribute from the owner.

        Removes both the dictionary entry and the corresponding attribute from the owner,
        maintaining synchronization.

        Args:
            key (str): The key to delete.
            
        Returns:
            None
            
        """

        super().__delitem__(key)  # Remove from dict
        if hasattr(self.owner, key):
            delattr(self.owner, key)  # Sync removal from instance
    def pop(self, key, *args):
        """
        Remove a key from the dictionary and owner's attributes, returning the value.

        Behaves like the built-in dict.pop(), but also deletes the attribute from the owner
        if it exists.

        Args:
            key (str): The key to remove.
            *args: Optional fallback value if the key does not exist.

        Returns:
            any: The value associated with the removed key, or the fallback value if the key did not exist.
        """

        value = super().pop(key, *args)  # Remove from dictionary
        if hasattr(self.owner, key):
            delattr(self.owner, key)  # Remove from instance attributes
        return value
    def update(self, *args, **kwargs):
        """
        Update the dictionary with new key-value pairs and sync them to the owner's attributes.

        This method extends the dictionary update logic to ensure that any added or modified
        keys are also set as attributes on the owner object.

        Args:
            *args: Accepts a dictionary or iterable of key-value pairs.
            **kwargs: Additional keyword pairs to add.
            
        Returns:
            None
        """

        super().update(*args, **kwargs)  # Update dict
        for key, value in self.items():
            setattr(self.owner, key, value)  # Sync attributes


class JSONGrapherDataSeries(dict): #inherits from dict.
    def __init__(self, uid="", name="", trace_style="", x=None, y=None, **kwargs):
        """
        Initializes a JSONGrapher data_series object which is a dictionary with custom functions and synchronized attribute-style access.

        This constructor sets default fields such as 'uid', 'name', 'trace_style', 'x', and 'y',
        and allows additional configuration via keyword arguments. The underlying structure behaves
        like both a dictionary and an object with attributes, supporting synced access patterns.

        Here are some fields that can be included, with example values.

        "uid": data_series_dict["uid"] = "123ABC",  # (string) a unique identifier
        "name": data_series_dict["name"] = "Sample Data Series",  # (string) name of the data_series
        "trace_style": data_series_dict["trace_style"] = "scatter",  # (string) type of trace (e.g., scatter, bar)
        "x": data_series_dict["x"] = [1, 2, 3, 4, 5],  # (list) x-axis values
        "y": data_series_dict["y"] = [10, 20, 30, 40, 50],  # (list) y-axis values
        "mode": data_series_dict["mode"] = "lines",  # (string) plot mode (e.g., "lines", "markers")
        "marker_size": data_series_dict["marker"]["size"] = 6,  # (integer) marker size
        "marker_color": data_series_dict["marker"]["color"] = "blue",  # (string) marker color
        "marker_symbol": data_series_dict["marker"]["symbol"] = "circle",  # (string) marker shape/symbol
        "line_width": data_series_dict["line"]["width"] = 2,  # (integer) line thickness
        "line_dash": data_series_dict["line"]["dash"] = "solid",  # (string) line style (solid, dash, etc.)
        "opacity": data_series_dict["opacity"] = 0.8,  # (float) transparency level (0-1)
        "visible": data_series_dict["visible"] = True,  # (boolean) whether the trace is visible
        "hoverinfo": data_series_dict["hoverinfo"] = "x+y",  # (string) format for hover display
        "legend_group": data_series_dict["legend_group"] = None,  # (string or None) optional grouping for legend


        Args:
            uid (str, optional): Unique identifier for the data_series. Defaults to an empty string.
            name (str, optional): Display name of the series. Defaults to an empty string.
            trace_style (str, optional): Type of plot trace (e.g., 'scatter', 'bar'). Defaults to an empty string.
            x (list, optional): X-axis data values. Defaults to an empty list.
            y (list, optional): Y-axis data values. Defaults to an empty list.
            **kwargs: Additional optional plot configuration (e.g., mode, marker, line, opacity).

        Example Fields Supported via kwargs:
            - mode: Plot mode such as "lines", "markers", or "lines+markers".
            - marker: Dictionary with subfields like "size", "color", and "symbol".
            - line: Dictionary with subfields like "width" and "dash".
            - opacity: Float value for transparency (0 to 1).
            - visible: Boolean to control trace visibility.
            - hoverinfo: String format for hover data.
            - legend_group: Optional grouping label for legends.
            - text: String or list of annotations.
        """
        super().__init__()  # Initialize as a dictionary

        # Default trace properties
        self.update({
            "uid": uid,
            "name": name,
            "trace_style": trace_style,
            "x": list(x) if x else [],
            "y": list(y) if y else []
        })

        # Include any extra keyword arguments passed in
        self.update(kwargs)

    def update_while_preserving_old_terms(self, series_dict):
        """
        Updates the current data_series dictionary with new values while retaining previously set terms that are not overwritten.

        This method applies a partial update to the internal dictionary by using the built-in `update()` method.
        Existing keys in `series_dict` will overwrite corresponding keys in the object, while all other existing
        keys and values will be preserved. Attributes on the owning object remain synchronized.

        Args:
            series_dict (dict): A dictionary containing updated fields for the data_series.

        Example:
            # Before: {'x': [1, 2], 'color': 'blue'}
            # After update_while_preserving_old_terms({'x': [3, 4]}): {'x': [3, 4], 'color': 'blue'}
        """
        self.update(series_dict)

    def get_data_series_dict(self):
        
        """
        Returns the underlying dictionary representation of the data_series dictionary.

        This method provides a clean snapshot of the current state of the data_series object
        by converting it into a standard Python dictionary. It is useful for serialization,
        debugging, or passing the data to plotting libraries like Plotly.

        Returns:
            dict: A dictionary containing all data fields of the series.
        """
        return dict(self)

    def set_x_values(self, x_values):
        """
        Updates the x-axis data for the series with a new set of values.

        This method replaces the current list of x-values in the data_series. If no values are provided 
        (i.e., None or empty), it safely defaults to an empty list. The update is synchronized through 
        the internal dictionary mechanism for consistency.

        Args:
            x_values (list): A list of numerical or categorical values to assign to the 'x' axis.
        """
        self["x"] = list(x_values) if x_values else []

    def set_y_values(self, y_values):
        """
        Updates the y-axis data for the series with a new set of values.

        This method replaces the current list of y-values in the data_series. If no values are provided 
        (i.e., None or empty), it defaults to an empty list. The assignment ensures consistency with the 
        internal dictionary and allows for flexible input formats.

        Args:
            y_values (list): A list of numerical or categorical values to assign to the 'y' axis.
        """
        self["y"] = list(y_values) if y_values else []

    def set_z_values(self, z_values):
        """
        Updates the z-axis data for the series with a new set of values.

        This method replaces the current list of z-values in the data_series. If no values are provided 
        (i.e., None or empty), it safely defaults to an empty list. The update is synchronized through 
        the internal dictionary mechanism for consistency.

        Args:
            z_values (list): A list of numerical or categorical values to assign to the 'z' axis.
        """
        self["z"] = list(z_values) if z_values else []


    def set_name(self, name):
        """
        Sets the name of the data_series to the provided value.

        This method assigns a human-readable identifier or label to the data_series, which is 
        typically used for legend display and trace identification in visualizations.

        Args:
            name (str): The new name or label to assign to the data_series.
        """
        self["name"] = name

    def set_uid(self, uid):
        """
        Sets or updates the unique identifier (UID) for the data_series.

        This method assigns a UID to the data_series, which can be used to uniquely identify
        the trace within a larger figure or dataset. UIDs are helpful for referencing, comparing,
        or updating specific traces, especially in dynamic or interactive plotting environments.

        Args:
            uid (str): A unique identifier string for the data_series.
        """
        self["uid"] = uid

    def set_trace_style(self, style):
        """
        Updates the trace style of the data_series to control its rendering behavior.

        This method sets the 'trace_style' field, which typically defines how the data_series
        appears visually in plots (e.g., 'scatter', 'bar', 'scatter_line', 'scatter_spline').

        Args:
            style (str): A string representing the desired visual trace style for plotting.
        """
        self["trace_style"] = style

    def set_marker_symbol(self, symbol):
        """
        Sets the marker symbol for data points by delegating to the internal set_marker_shape method.

        This method provides a user-friendly way to define the visual marker used for plotting individual
        points on the graph. The symbol parameter is passed directly to set_marker_shape, which handles
        the internal logic for updating the marker settings.

        Args:
            symbol (str): The symbol to use for markers (e.g., "circle", "square", "diamond", "x", "star").
        """
        self.set_marker_shape(shape=symbol)

    def set_marker_shape(self, shape):
        """
        Sets the visual symbol used for markers in the data series.

        This method updates the shape of marker symbols (used in scatter plots, etc.) 
        based on supported Plotly marker types. It ensures the internal marker dictionary 
        exists and assigns the specified symbol string to the 'symbol' field.

        Supported Shapes:
            - circle, square, diamond, cross, x
            - triangle-up, triangle-down, triangle-left, triangle-right
            - pentagon, hexagon, star, hexagram
            - star-triangle-up, star-triangle-down, star-square, star-diamond
            - hourglass, bowtie

        Args:
            shape (str): The name of the marker symbol to use. Must be one of the supported Plotly shapes.
        """
        self.setdefault("marker", {})["symbol"] = shape

    def add_xy_data_point(self, x_val, y_val):
        """
        Adds a new x-y data point to the data_series.

        This method appends the provided x and y values to their respective lists
        within the internal data structure. It is typically used to incrementally
        build or extend a dataset for plotting or analysis.

        Args:
            x_val (any): The x-axis value of the data point.
            y_val (any): The y-axis value of the data point.
        """
        self["x"].append(x_val)
        self["y"].append(y_val)

    def add_xyz_data_point(self, x_val, y_val, z_val):
        """
        Adds a new x-y-z data point to the data_series.

        This method appends the provided x and y and z values to their respective lists
        within the internal data structure. It is typically used to incrementally
        build or extend a dataset for plotting or analysis.

        Args:
            x_val (any): The x-axis value of the data point.
            y_val (any): The y-axis value of the data point.
            z_val (any): The z-axis value of the data point.
        """
        self["x"].append(x_val)
        self["y"].append(y_val)
        self["z"].append(z_val)


    def set_marker_size(self, size):
        """
        Updates the size of the markers used in the data_series visualization.

        This method modifies the 'size' field within the 'marker' dictionary of the data_series.
        If the 'marker' dictionary doesn't already exist, it is created. The marker size controls 
        the visual prominence of data points in charts like scatter plots.

        Args:
            size (int or float): The desired marker size, typically a positive number.
        """
        self.setdefault("marker", {})["size"] = size

    def set_marker_color(self, color):
        """
        Sets the color of the markers in the data_series visualization.

        This method ensures that the 'marker' dictionary exists within the data_series,
        and then updates its 'color' key with the provided value. Marker color can be a
        standard named color (e.g., "blue"), a hex code (e.g., "#1f77b4"), or an RGB/RGBA string.

        Args:
            color (str): The color to use for the data_series markers.
        """
        self.setdefault("marker", {})["color"] = color

    def set_mode(self, mode):
        """
        Sets the rendering mode for the data_series, correcting common input patterns.

        This method updates the 'mode' field to control how data points are visually represented 
        in plots (e.g., as lines, markers, text, or combinations). If the user accidentally uses 
        "line" instead of "lines", it automatically corrects the term to maintain compatibility 
        with plotting libraries like Plotly.

        Supported Modes:
            - 'lines'
            - 'markers'
            - 'text'
            - 'lines+markers'
            - 'lines+text'
            - 'markers+text'
            - 'lines+markers+text'

        Args:
            mode (str): Desired rendering mode. Common typos like 'line' may be corrected.
        """
        if "line" in mode and "lines" not in mode:
            mode = mode.replace("line", "lines")
        self["mode"] = mode

    def set_annotations(self, text): #just a convenient wrapper.
        """
        Sets text annotations for the data_series by delegating to the internal set_text method.

        This is a convenience wrapper that allows assigning label text to individual data points 
        in the series. Annotations can enhance readability and provide contextual information 
        in visualizations such as tooltips or direct text labels on plots.

        Args:
            text (str or list): Annotation text for the data points. Can be a single string 
                                or a list of strings corresponding to each data point.
        """
        self.set_text(text) 

    def set_text(self, text):

        """
        Sets annotation text for each point in the data_series. The a list of text values must be provided, equal to
        the number of points. If a single string value is provided, it will be repeated to be the same for each point.

        This method allows the user to assign either a single string or a list of strings to annotate
        each point in the series. If a single string is provided, it is replicated to match the number
        of data points; otherwise, the provided list is used as-is. Useful for adding tooltips or labels.
        The number of values received being equal to the number of points is checked by comparing to the x values.

        Args:
            text (str or list): Annotation text—either a single string (applied to all points) or a list
                                of strings, one for each point in the series.
        """

        #text should be a list of strings teh same length as the data_series, one string per point.
        """Update the annotations with a list of text as long as the number of data points."""
        if text == type("string"): 
            text = [text] * len(self["x"])  # Repeat the text to match x-values length
        else:
            pass #use text directly    
        self["text"] = text


    def set_line_width(self, width):
        """
        Sets the width of the line used for the trace of the data_series.

        This method ensures that the 'line' dictionary exists within the data_series and then sets
        the 'width' attribute to the specified value. This affects the thickness of lines in charts
        like line plots and splines.

        Args:
            width (int or float): The thickness value for the line. Typically a positive number.
        """
        line = self.setdefault("line", {})
        line.setdefault("width", width)  # Ensure width is set

    def set_line_dash(self, dash_style):
        """
        Sets the dash style of the line used in the data_series visualization.

        This method modifies the 'dash' attribute inside the 'line' dictionary, which controls
        the appearance of the line in the chart. It allows for various visual styles, such as
        dashed, dotted, or solid lines, aligning with the supported Plotly dash patterns.

        Supported Styles:
            - 'solid'
            - 'dot'
            - 'dash'
            - 'longdash'
            - 'dashdot'
            - 'longdashdot'

        Args:
            dash_style (str): The desired dash pattern for the line. Must match one of Plotly’s accepted styles.
        """
        self.setdefault("line", {})["dash"] = dash_style

    def set_transparency(self, transparency_value):
        """
        Converts a transparency value into an opacity setting and applies it to the data_series.

        This method accepts a transparency value—ranging from 0 (fully opaque) to 1 (fully transparent)—
        and calculates the corresponding opacity value used by plotting libraries. It inverts the input
        so that increasing transparency reduces opacity.

        Args:
            transparency_value (float): A decimal between 0 and 1 where:
                - 0 means fully visible (opacity = 1),
                - 1 means fully invisible (opacity = 0),
                - intermediate values create partial see-through effects.
        """
        self["opacity"] = 1 - transparency_value

    def set_opacity(self, opacity_value):
        """
        Sets the opacity level for the data_series.

        This method directly assigns an opacity value to the data_series, which controls the visual
        transparency of the trace in the plot. An opacity of 1.0 means fully opaque, while 0.0 is fully
        transparent. Intermediate values allow for layering effects and visual blending.

        Args:
            opacity_value (float): A number between 0 (transparent) and 1 (opaque) representing the opacity level.
        """
        self["opacity"] = opacity_value

    def set_visible(self, is_visible):
        """
        Sets the visibility state of the data_series in the plot.

        This method allows control over how the trace is displayed. It accepts a boolean value
        or the string "legendonly" to indicate the desired visibility mode. This feature is 
        particularly useful for managing clutter in complex visualizations or toggling traces dynamically.

        Args:
            is_visible (bool or str): 
                - True → Fully visible in the plot.
                - False → Hidden entirely.
                - "legendonly" → Hidden from the plot but shown in the legend.
        """
        
        self["visible"] = is_visible

    def set_hoverinfo(self, hover_format):
        """
        Sets the formatting for hover labels in interactive visualizations.

        This method defines what information appears when the user hovers over data points in the plot.
        Accepted formats include combinations of "x", "y", "text", "name", etc., joined with "+" symbols.

        Example formats:
            - "x+y" → Shows x and y values
            - "x+text" → Shows x value and text annotation
            - "none" → Disables hover info

        Args:
            hover_format (str): A string specifying what data to display on hover.
        """
        self["hoverinfo"] = hover_format



class JSONGrapherRecord:
    """
    This class enables making JSONGrapher records. Each instance represents a structured JSON record for a graph.
    One can optionally provide an existing JSONGrapher record during creation to pre-populate the object.
    One can manipulate the fig_dict inside, directly, using syntax like Record.fig_dict["comments"] = ...
    One can also use syntax like Record["comments"] = ...  as some 'magic' synchronizes fields directlyin the Record with fields in the fig_dict.
    However, developers should usually use the syntax like Record.fig_dict, internally, to avoid any referencing mistakes.


    Arguments & Attributes (all are optional):
        comments (str): Can be used to put in general description or metadata related to the entire record. Can include citation links. Goes into the record's top level comments field.
        datatype: The datatype is the experiment type or similar, it is used to assess which records can be compared and which (if any) schema to compare to. Use of single underscores between words is recommended. This ends up being the datatype field of the full JSONGrapher file. Avoid using double underscores '__' in this field  unless you have read the manual about hierarchical datatypes. The user can choose to provide a URL to a schema in this field, rather than a dataype name. May have underscore, should not have spaces.
        graph_title: Title of the graph or the dataset being represented.
        data_objects_list (list): List of data series dictionaries to pre-populate the record. These may contain 'simulate' fields in them to call javascript source code for simulating on the fly.
        simulate_as_added: Boolean. True by default. If true, any data series that are added with a simulation field will have an immediate simulation call attempt.
        x_data: Single series x data values in a list or array-like structure. 
        y_data: Single series y data values in a list or array-like structure.
        x_axis_label_including_units: A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units . The dimensions of units can be multiple, such as mol/s. SI units are expected. Custom units must be inside  < > and at the beginning.  For example, (<frogs>*kg/s)  would be permissible. Units should be non-plural (kg instead of kgs) and should be abbreviated (m not meter). Use “^” for exponents. It is recommended to have no numbers in the units other than exponents, and to thus use (bar)^(-1) rather than 1/bar.
        y_axis_label_including_units: A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units . The dimensions of units can be multiple, such as mol/s. SI units are expected. Custom units must be inside  < > and at the beginning.  For example, (<frogs>*kg/s)  would be permissible. Units should be non-plural (kg instead of kgs) and should be abbreviated (m not meter). Use “^” for exponents. It is recommended to have no numbers in the units other than exponents, and to thus use (bar)^(-1) rather than 1/bar.
        layout: A dictionary defining the layout of the graph, including axis titles,
                comments, and general formatting options.
    
    Methods:
        add_data_series: Adds a new data_series to the record.
        add_data_series_as_equation: Adds a new equation to plot, which will be evaluated on the fly.
        set_layout_fields: Updates the layout configuration for the graph.
        export_to_json_file: Saves the entire record (comments, datatype, data, layout) as a JSON file.
        populate_from_existing_record: Populates the attributes from an existing JSONGrapher record.
    """

    def __init__(self, comments="", graph_title="", datatype="", data_objects_list = None, simulate_as_added = True, evaluate_equations_as_added = True, x_data=None, y_data=None, x_axis_label_including_units="", y_axis_label_including_units ="", plot_style ="", layout=None, existing_JSONGrapher_record=None):
        """
        Initializes a JSONGrapherRecord object that represents a structured fig_dict for graphing.

        Optionally populates fields from an existing JSONGrapher record and applies immediate processing
        such as simulation or equation evaluation on data series when applicable.

        Args:
            comments (str, optional): General description or metadata for the record.
            graph_title (str, optional): Title for the graph; is put into the layout title field.
            datatype (str, optional): The datatype is the experiment type or similar, it is used to assess which records can be compared and which (if any) schema to compare to. Use of single underscores between words is recommended. This ends up being the datatype field of the full JSONGrapher file. Avoid using double underscores '__' in this field  unless you have read the manual about hierarchical datatypes. The user can choose to provide a URL to a schema in this field, rather than a dataype name. May have underscore, should not have spaces.
            data_objects_list (list, optional): List of data_series dictionaries to pre-populate the record.
            simulate_as_added (bool, optional): If True, attempts simulation on data with 'simulate' fields.
            evaluate_equations_as_added (bool, optional): True by default. If true, any data series that are added with a simulation field will have an immediate simulation call attempt.
            x_data (list or array-like, optional): x-axis values for a single data series.
            y_data (list or array-like, optional): y-axis values for a single data series.
            x_axis_label_including_units (str, optional): x-axis label with units in parentheses. A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units . The dimensions of units can be multiple, such as mol/s. SI units are expected. Custom units must be inside  < > and at the beginning.  For example, (<frogs>*kg/s)  would be permissible. Units should be non-plural (kg instead of kgs) and should be abbreviated (m not meter). Use “^” for exponents. It is recommended to have no numbers in the units other than exponents, and to thus use (bar)^(-1) rather than 1/bar.
            y_axis_label_including_units (str, optional): y-axis label with units in parentheses. A string with units provided in parentheses. Use of multiplication "*" and division "/" and parentheses "( )" are allowed within in the units . The dimensions of units can be multiple, such as mol/s. SI units are expected. Custom units must be inside  < > and at the beginning.  For example, (<frogs>*kg/s)  would be permissible. Units should be non-plural (kg instead of kgs) and should be abbreviated (m not meter). Use “^” for exponents. It is recommended to have no numbers in the units other than exponents, and to thus use (bar)^(-1) rather than 1/bar.
            plot_style (str, optional): Style applied to the overall plot; stored in fig_dict["plot_style"].
            layout (dict, optional): layout_style dictionary configuring graph appearance.
            existing_JSONGrapher_record (dict, optional): Dictionary representing an existing JSONGrapher record 
                to populate the new or current instance.

        Raises:
            KeyError: If simulation attempts fail due to missing expected keys.
            Exception: Catches and logs unexpected errors during simulation or equation evaluation.

        Side Effects:
            - Updates self.fig_dict with layout_style, data_series dictionaries, and metadata.
            - Applies optional simulation or evaluation to fig_dict.
            - Initializes a hints_dictionary to guide field-level edits within the fig_dict.

        """
        if layout == None: #it's bad to have an empty dictionary or list as a python argument.
            layout = {}

        # Assign self.fig_dict in a way that it will push any changes to it into the class instance.
        self.fig_dict = {}

        # If receiving a data_objects_list, validate it.
        if data_objects_list:
            validate_plotly_data_list(data_objects_list)  # Call a function from outside the class.

        # If receiving axis labels, validate them.
        if x_axis_label_including_units:
            validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=False)
        if y_axis_label_including_units:
            validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=False)

        self.fig_dict.update( {
            "comments": comments,  # Top-level comments
            "jsongrapher": "To plot this file, go to www.jsongrapher.com and drag this file into your browser, or use the python version of JSONGrapher. File created with python Version " + JSONGrapher.version.__version__,
            "datatype": datatype,  # Top-level datatype (datatype)
            "layout": layout if layout else {
                "title": {"text": graph_title},
                "xaxis": {"title": {"text": x_axis_label_including_units}},
                "yaxis": {"title": {"text": y_axis_label_including_units}}
                   },
            "data": data_objects_list if data_objects_list else []  # Data series list                
            }
            )

        if plot_style !="":
            self.fig_dict["plot_style"] = plot_style
        if simulate_as_added:  # Will try to simulate, but because this is the default, will use a try-except rather than crash the program.
            try:
                self.fig_dict = simulate_as_needed_in_fig_dict(self.fig_dict)
            except KeyError:
                pass  # Handle missing key issues gracefully
            except Exception as e: # This is so VS code pylint does not flag this line: pylint: disable=broad-except
                print(f"Unexpected error: {e}")  # Logs any unhandled errors

        if evaluate_equations_as_added:  # Will try to evaluate, but because this is the default, will use a try-except rather than crash the program.
            try:
                self.fig_dict = evaluate_equations_as_needed_in_fig_dict(self.fig_dict)
            except Exception as e: # This is so VS code pylint does not flag this line. pylint: disable=broad-except, disable=unused-variable
                pass 
        # Populate attributes if an existing JSONGrapher record is provided as a dictionary.
        if existing_JSONGrapher_record:
            self.populate_from_existing_record(existing_JSONGrapher_record)

        # Initialize the hints dictionary, for use later, since the actual locations in the JSONRecord can be non-intuitive.
        self.hints_dictionary = {}
        # Adding hints. Here, the keys are the full field locations within the record.
        self.hints_dictionary["['comments']"] = "Use Record.set_comments() to populate this field. Can be used to put in a general description or metadata related to the entire record. Can include citations and links. Goes into the record's top-level comments field."
        self.hints_dictionary["['datatype']"] = "Use Record.set_datatype() to populate this field. This is the datatype, like experiment type, and is used to assess which records can be compared and which (if any) schema to compare to. Use of single underscores between words is recommended. Avoid using double underscores '__' in this field unless you have read the manual about hierarchical datatypes. The user can choose to provide a URL to a schema in this field rather than a datatype name."
        self.hints_dictionary["['layout']['title']['text']"] = "Use Record.set_graph_title() to populate this field. This is the title for the graph."
        self.hints_dictionary["['layout']['xaxis']['title']['text']"] = "Use Record.set_x_axis_label() to populate this field. This is the x-axis label and should have units in parentheses. The units can include multiplication '*', division '/' and parentheses '( )'. Scientific and imperial units are recommended. Custom units can be contained in pointy brackets '< >'."  # x-axis label
        self.hints_dictionary["['layout']['yaxis']['title']['text']"] = "Use Record.set_y_axis_label() to populate this field. This is the y-axis label and should have units in parentheses. The units can include multiplication '*', division '/' and parentheses '( )'. Scientific and imperial units are recommended. Custom units can be contained in pointy brackets '< >'."

    ##Start of section of class code that allows class to behave like a dictionary and synchronize with fig_dict ##
    #The __getitem__ and __setitem__ functions allow the class instance to behave 'like' a dictionary without using super.
    #The below functions allow the JSONGrapherRecord to populate the self.fig_dict each time something is added inside.
    #That is, if someone uses something like Record["comments"]="frog", it will also put that into self.fig_dict

    def __getitem__(self, key):
        """
        Retrieves the value associated with the specified key from the fig_dict.

        Args:
            key: The field name to look up in the fig_dict.

        Returns:
            The value mapped to the specified key within the fig_dict.
        """
        return self.fig_dict[key]  # Direct access

    def __setitem__(self, key, value):
        """
        Sets the specified key in the fig_dict to the given value.

        Args:
            key: The field name to assign or update in the fig_dict.
            value: The value to associate with the specified key in the fig_dict.
        """
        self.fig_dict[key] = value  # Direct modification

    def __delitem__(self, key):
        """
        Deletes the specified key and its associated value from the fig_dict.

        Args:
            key: The field name to remove from the fig_dict.
        """
        del self.fig_dict[key]  # Support for deletion

    def __iter__(self):
        """
        Returns an iterator over the keys in the fig_dict.

        Returns:
            An iterator that allows traversal of all top-level keys in fig_dict.
        """
        return iter(self.fig_dict)  # Allow iteration

    def __len__(self):
        """
        Returns the number of top-level fields (keys) currently stored in the fig_dict.

        Returns:
            The count of top-level fields (keys) present in the fig_dict.
        """
        return len(self.fig_dict)  # Support len()

    def pop(self, key, default=None):
        """
        Removes the specified key and returns its value from the fig_dict.

        Args:
            key: The field name to remove from the fig_dict.
            default (optional): Value to return if the key is not found.

        Returns:
            The value previously associated with the key, or the specified default if the key was absent.
        """
        return self.fig_dict.pop(key, default)  # Implement pop()

    def keys(self):
        """
        Returns a dynamic, read-only view of all top-level keys in the fig_dict.

        Returns:
            A view object that reflects the current set of keys in the fig_dict.
        """
        return self.fig_dict.keys()  # Dictionary-like keys()

    def values(self):
        """
        Returns a dynamic, read-only view of all values stored in the fig_dict.

        Returns:
            A view object that reflects the current set of values in the fig_dict.
        """
        return self.fig_dict.values()  # Dictionary-like values()

    def items(self):
        """
        Returns a dynamic, read-only view of all key-value pairs in the fig_dict.

        Returns:
            A view object that reflects the current set of key-value pairs in the fig_dict.
        """
        return self.fig_dict.items()  # Dictionary-like items()
    
    def update(self, *args, **kwargs):
        """
        Updates the fig_dict with new key-value pairs.

        Args:
            *args: Positional arguments containing mappings or iterable key-value pairs.
            **kwargs: Arbitrary keyword arguments to be added as key-value pairs in the fig_dict.
        """
        self.fig_dict.update(*args, **kwargs)


    ##End of section of class code that allows class to behave like a dictionary and synchronize with fig_dict ##

    #this function enables printing the current record.
    def __str__(self):
        """
        Returns a JSON-formatted string representation of the fig_dict with 4-space "pretty-print" indentation.

        Returns:
            str: A readable JSON string of the record's contents.

        Notes:
            This method does not perform automatic consistency updates or validation.
            It is recommended to use the syntax RecordObject.print_to_inspect()
            which will make automatic consistency updates and validation checks to the record before printing.

        """
        print("Warning: Printing directly will return the raw record without some automatic updates. It is recommended to use the syntax RecordObject.print_to_inspect() which will make automatic consistency updates and validation checks to the record before printing.")
        return json.dumps(self.fig_dict, indent=4)


    def add_data_series(self, series_name, x_values=None, y_values=None, simulate=None, simulate_as_added=True, comments="", trace_style=None, uid="", line=None, extra_fields=None):
        """
        Adds a new x,y data series to the fig_dict with optional metadata, styling, and simulation support.

        Args:
            series_name (str): Label for the data series to appear in the graph.
            x_values (list or array-like, optional): x-axis values. Defaults to an empty list.
            y_values (list or array-like, optional): y-axis values. Defaults to an empty list.
            simulate (dict, optional): Dictionary specifying on-the-fly simulation parameters.
            simulate_as_added (bool): If True, and if the 'simulate' field is present, then attempts to simulate this series immediately upon addition.
            comments (str): Description or annotations tied to the data series.
            trace_style (str or dict): trace_style for the data_series (e.g., scatter, line, spline, bar).
            uid (str): Optional unique ID (e.g., DOI) linked to the series.
            line (dict): Dictionary of visual line properties like shape or width.
            extra_fields (dict): A dictionary with custom keys and values to add into the data_series dictionary.

        Returns:
            dict: The newly constructed data_series dictionary.

        Notes:
            - There is also an 'implied' return in that the new data_series_dict is added to the JSONGrapher object's fig_dict.
            - Inputs are converted to lists to ensure consistency with expected format.
            - Simulation failures are silently ignored to maintain program flow.
            - The returned object allows extended editing of visual and structural properties.
        """
        # series_name: Name of the data series.
        # x: List of x-axis values. Or similar structure.
        # y: List of y-axis values. Or similar structure.
        # simulate: This is an optional field which, if used, is a JSON object with entries for calling external simulation scripts.
        # simulate_as_added: Boolean for calling simulation scripts immediately.
        # comments: Optional description of the data series.
        # trace_style: Type of the data (e.g., scatter, line, scatter_spline, spline, bar).
        # line: Dictionary describing line properties (e.g., shape, width).
        # uid: Optional unique identifier for the series (e.g., a DOI).
        # extra_fields: Dictionary containing additional fields to add to the series.
        #Should not have mutable objects initialized as defaults, so putting them in below.
        if x_values is None:
            x_values = []
        if y_values is None:
            y_values = []
        if simulate is None:
            simulate = {}

        x_values = list(x_values)
        y_values = list(y_values)

        data_series_dict = {
            "name": series_name,
            "x": x_values, 
            "y": y_values,
        }

        #Add optional inputs.
        if len(comments) > 0:
            data_series_dict["comments"] = comments
        if len(uid) > 0:
            data_series_dict["uid"] = uid
        if line: #This checks variable is not None, and not empty.
            data_series_dict["line"] = line
        if trace_style: #This checks variable is not None, and not empty.
            data_series_dict['trace_style'] = trace_style
        #add simulate field if included.
        if simulate:
            data_series_dict["simulate"] = simulate
        # Add extra fields if provided, they will be added.
        if extra_fields:
            data_series_dict.update(extra_fields)

        #make this a JSONGrapherDataSeries class object, that way a person can use functions to do things like change marker size etc. more easily.
        JSONGrapher_data_series_object = JSONGrapherDataSeries()
        JSONGrapher_data_series_object.update_while_preserving_old_terms(data_series_dict)
        data_series_dict = JSONGrapher_data_series_object
        #Add to the JSONGrapherRecord class object's data list.
        self.fig_dict["data"].append(data_series_dict) #implied return.

        if simulate_as_added: #will try to simulate. But because this is the default, will use a try and except rather than crash program.
            try:
                #we use simulate_specific_data_series_by_index rather than just the simulate funciton because we want unit scaling and clearing of labels as needed.
                data_series_index = len(self.fig_dict["data"]) - 1
                data_series_dict = simulate_specific_data_series_by_index(fig_dict=self.fig_dict, data_series_index=data_series_index)
            except Exception as e: # This is so VS code pylint does not flag this line. pylint: disable=broad-except, disable=unused-variable
                pass
        return data_series_dict

    def add_data_series_as_simulation(self, series_name,graphical_dimensionality, x_values=None,y_values=None, simulate_dict=None,simulate_as_added=True,comments="",trace_style=None,uid="",line=None,extra_fields=None):
        """
        Adds a simulation-style data_series using the `add_data_series` method.

        This method wraps the provided series data and simulation configuration,
        including graphical dimensionality and style options, and forwards them
        to `add_data_series`.

        Args:
            series_name (str): Name of the data_series to be added.
            graphical_dimensionality (int): Indicates how the simulation should be visualized.
            x_values (list, optional): List of x-axis values. Defaults to empty list if None.
            y_values (list, optional): List of y-axis values. Defaults to empty list if None.
            simulate_dict (dict, optional): Dictionary containing simulation metadata. 
                Will be initialized if not provided. The key 'graphical_dimensionality' 
                is always set based on the input.
            simulate_as_added (bool, optional): Whether to mark the simulation as added. Defaults to True.
            comments (str, optional): Additional notes or annotations for the data_series.
            trace_style (dict, optional): Dictionary specifying visual trace_style.
            uid (str, optional): Unique identifier for the data_series.
            line (Any, optional): Line formatting information for the plot trace.
            extra_fields (dict, optional): Extra metadata fields to include.

        Returns:
            Any: Result of calling `add_data_series` with the provided arguments.
        """
        if x_values is None:
            x_values = []
        if y_values is None:
            y_values = []
        if simulate_dict is None:
            simulate_dict = {}

        simulate_dict["graphical_dimensionality"] = int(graphical_dimensionality)

        return self.add_data_series(
            series_name=series_name,
            x_values=x_values,
            y_values=y_values,
            simulate=simulate_dict,
            simulate_as_added=simulate_as_added,
            comments=comments,
            trace_style=trace_style,
            uid=uid,
            line=line,
            extra_fields=extra_fields
        )

    def add_data_series_as_equation( self, series_name, graphical_dimensionality, x_values=None, y_values=None, equation_dict=None, evaluate_equations_as_added=True, comments="", trace_style=None, uid="",line=None,extra_fields=None):
        """
        Adds an equation-style data_series using the `add_data_series` method.

        This method incorporates the equation metadata into extra_fields and 
        optionally evaluates the equations immediately after adding the data_series.

        Args:
            series_name (str): Name of the data_series to be added.
            graphical_dimensionality (int): Visual representation dimensionality.
            x_values (list, optional): List of x-axis values. Defaults to an empty list.
            y_values (list, optional): List of y-axis values. Defaults to an empty list.
            equation_dict (dict, optional): Dictionary representing equation metadata.
                The key 'graphical_dimensionality' is automatically set.
            evaluate_equations_as_added (bool, optional): Whether to evaluate the equation 
                immediately after adding. Defaults to True.
            comments (str, optional): Additional notes or annotations for the data_series.
            trace_style (dict, optional): Dictionary specifying visual trace_style.
            uid (str, optional): Unique identifier for the data_series.
            line (Any, optional): Line formatting information for the plot trace.
            extra_fields (dict, optional): Dictionary for extra metadata; updated with equation_dict.

        Returns:
            Any: Result from `add_data_series`, potentially updated in fig_dict after evaluation.
        """
        if x_values is None:
            x_values = []
        if y_values is None:
            y_values = []
        if equation_dict is None:
            equation_dict = {}

        # Add required key
        equation_dict["graphical_dimensionality"] = int(graphical_dimensionality)

        # Prepare extra_fields with equation dict
        if extra_fields is None:
            extra_fields = {}
        extra_fields["equation"] = equation_dict

        # Add the series
        data_series = self.add_data_series(
            series_name=series_name,
            x_values=x_values,
            y_values=y_values,
            comments=comments,
            trace_style=trace_style,
            uid=uid,
            line=line,
            extra_fields=extra_fields
        )

        # Evaluate if required
        if evaluate_equations_as_added:
            try:
                index = len(self.fig_dict["data"]) - 1
                self.fig_dict = evaluate_equation_for_data_series_by_index(self.fig_dict, index)
            except Exception:
                pass

        return data_series

        
    def change_data_series_name(self, series_index, series_name):
        """
        Renames a data series within the fig_dict at the specified index.

        Args:
            series_index (int): Index of the target data series in the fig_dict["data"] list.
            series_name (str): New name to assign to the data series.

        Notes:
            - This updates the 'name' field of the selected data_series dictionary.
        """
        self.fig_dict["data"][series_index]["name"] = series_name

    #this function forces the re-simulation of a particular dataseries.
    #The simulator link will be extracted from the record, by default.
    def simulate_data_series_by_index(self, data_series_index, simulator_link='', verbose=False):
        """
        Forces re-simulation of a specific data_series within the fig_dict using its index, if the data_series dictionary has a 'simulate' field.

        Args:
            data_series_index (int): Index of the data series in the fig_dict["data"] list to re-simulate.
            simulator_link (str, optional): Custom path or URL to override the default simulator. If not provided,
                the link is extracted from the 'simulate' field in the data_series dictionary.
            verbose (bool): If True, prints performs the simulation with the verbose flag turned on.

        Returns:
            dict: The updated data_series dictionary reflecting the results of the re-simulation.

        Notes:
            - There is an 'implied return': fig_dict is replaced in-place with its updated version after simulation.
            - Useful when recalculating output for a data_series with a defined 'simulate' field.
        """
        self.fig_dict = simulate_specific_data_series_by_index(fig_dict=self.fig_dict, data_series_index=data_series_index, simulator_link=simulator_link, verbose=verbose)
        data_series_dict = self.fig_dict["data"][data_series_index] #implied return
        return data_series_dict #Extra regular return
    #this function returns the current record.

    def evaluate_equation_of_data_series_by_index(self, series_index, equation_dict = None, verbose=False):
        """
        Forces evaluates the equation associated with a data series in the fig_dict by its index.

        Args:
            series_index (int): Index of the data series within fig_dict["data"] to evaluate the equation for.
            equation_dict (dict, optional): An equation dictionary to overwrite or assign as the data_series dictionary before evaluation.
            verbose (bool): If True, passes the verbose flag forward for during the equation evalution.

        Returns:
            dict: The data_series dictionary updated with evaluated values.

        Notes:
            - There is also an 'implied' return in that the new data_series_dict is added to the JSONGrapher object's fig_dict.
            - If equation_dict is provided, it is assigned to the data_series prior to evaluation.
            - The fig_dict is updated in-place with the evaluation results.
            - Ensure the series at the given index contains or receives a valid equation structure.
        """
        if equation_dict != None:
            self.fig_dict["data"][series_index]["equation"] = equation_dict
        data_series_dict = self.fig_dict["data"][series_index]
        self.fig_dict = evaluate_equation_for_data_series_by_index(fig_dict=self.fig_dict, data_series_index=data_series_dict, verbose=verbose) #implied return.
        return data_series_dict #Extra regular return

    #this function returns the current record.       
    def get_record(self):
        """
        Retrieves the full fig_dict representing the current JSONGrapher record.

        Returns:
            dict: The fig_dict for the current JSONGrapher record.
        """
        return self.fig_dict
    #The update_and_validate function will clean for plotly.
    #TODO: the internal recommending "print_to_inspect" function should, by default, exclude printing the full dictionaries of the layout_style and the trace_collection_style.
    def print_to_inspect(self, update_and_validate=True, validate=True, clean_for_plotly = True, remove_remaining_hints=False):
        """
        Prints the current fig_dict in a human-readable JSON format, with optional consistency checks.

        Args:
            update_and_validate (bool): If True (default), applies automatic updates and data cleaning before printing.
            validate (bool): If True (default), runs validation even if updates are skipped.
            clean_for_plotly (bool): If True (default), adjusts structure for compatibility with rendering tools.
            remove_remaining_hints (bool): If True, strips hint-related metadata before output.

        Notes:
            - Recommended over __str__ for reviewing records with validated and updated content.
            - Future updates may include options to limit verbosity (e.g., omit layout_style and trace_style sections).
        """
        if remove_remaining_hints == True:
            self.remove_hints()
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record(clean_for_plotly=clean_for_plotly)
        elif validate: #this will validate without doing automatic updates.
            self.validate_JSONGrapher_record()
        print(json.dumps(self.fig_dict, indent=4))

    def populate_from_existing_record(self, existing_JSONGrapher_record):
        """
        Populates the fig_dict using an existing JSONGrapher record.

        Args:
            existing_JSONGrapher_record (dict or JSONGrapherRecord): Source record to use for populating the current instance.

        """
        #While we expect a dictionary, if a JSONGrapher ojbect is provided, we will simply pull the dictionary out of that.
        if isinstance(existing_JSONGrapher_record, dict): 
            if "comments" in existing_JSONGrapher_record:   self.fig_dict["comments"] = existing_JSONGrapher_record["comments"]
            if "datatype" in existing_JSONGrapher_record:      self.fig_dict["datatype"] = existing_JSONGrapher_record["datatype"]
            if "data" in existing_JSONGrapher_record:       self.fig_dict["data"] = existing_JSONGrapher_record["data"]
            if "layout" in existing_JSONGrapher_record:     self.fig_dict["layout"] = existing_JSONGrapher_record["layout"]
        else:
            self.fig_dict = existing_JSONGrapher_record.fig_dict


    #the below function takes in existin JSONGrpher record, and merges the data in.
    #This requires scaling any data as needed, according to units.
    def merge_in_JSONGrapherRecord(self, fig_dict_to_merge_in):
        """
        Merges data from another JSONGrapher record into the current fig_dict with appropriate unit scaling.
            - Extracts x and y axis units from both records and calculates scaling ratios.
            - Applies uniform scaling to all data_series dictionaries in the incoming record.
            - Supports string and object-based inputs by auto-converting them into a usable fig_dict format.
            - New data series are deep-copied and appended to the current fig_dict["data"] list.

        Args:
            fig_dict_to_merge_in (dict, str, or JSONGrapherRecord): Source record to merge. Can be a fig_dict dictionary,
                a JSON-formatted string of a fig_dict, or a JSONGrapherRecord object instance.

        """
        import copy
        fig_dict_to_merge_in = copy.deepcopy(fig_dict_to_merge_in)
        if type(fig_dict_to_merge_in) == type({}):
            pass #this is what we are expecting.
        elif type(fig_dict_to_merge_in) == type("string"):
            fig_dict_to_merge_in = json.loads(fig_dict_to_merge_in)
        else: #this assumpes there is a JSONGrapherRecord type received. 
            fig_dict_to_merge_in = fig_dict_to_merge_in.fig_dict
        #Now extract the units of the current record.
        first_record_x_label = self.fig_dict["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
        first_record_y_label = self.fig_dict["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
        first_record_x_units = separate_label_text_from_units(first_record_x_label)["units"]
        first_record_y_units = separate_label_text_from_units(first_record_y_label)["units"]
        #Get the units of the new record.
        this_record_x_label = fig_dict_to_merge_in["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
        this_record_y_label = fig_dict_to_merge_in["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
        this_record_x_units = separate_label_text_from_units(this_record_x_label)["units"]
        this_record_y_units = separate_label_text_from_units(this_record_y_label)["units"]
        #now get the ratio of the units for this record relative to the first record.
        x_units_ratio = get_units_scaling_ratio(this_record_x_units, first_record_x_units)
        y_units_ratio = get_units_scaling_ratio(this_record_y_units, first_record_y_units)
        #A record could have more than one data series, but they will all have the same units.
        #Thus, we use a function that will scale all of the dataseries at one time.
        scaled_fig_dict = scale_fig_dict_values(fig_dict_to_merge_in, x_units_ratio, y_units_ratio)
        #now, add the scaled data objects to the original one.
        #This is fairly easy using a list extend.
        self.fig_dict["data"].extend(scaled_fig_dict["data"])
   
    def import_from_dict(self, fig_dict):
        """
        Imports a complete fig_dict into the current JSONGrapherRecord instance, replacing its contents.
            - Any current fig_dict is entirely overwritten without merging or validation.

        Args:
            fig_dict (dict): A JSONGrapher record fig_dict.

        """
        self.fig_dict = fig_dict
    
    def import_from_file(self, record_filename_or_object):
        """
        Imports a record from a supported file type or dictionary to create a fig_dict.
            - Automatically detects file type via extension when a string path is provided.
            - CSV/TSV content is handled using import_from_csv with delimiter selection.
            - JSON files and dictionaries are passed directly to import_from_json.

        Args:
            record_filename_or_object (str or dict): A file path for a CSV, TSV, or JSON file,
                or a dictionary representing a JSONGrapher record.

        Returns:
            dict: The fig_dict created or extracted from the file or provided object.

        Raises:
            ValueError: If the file extension is unsupported (not .csv, .tsv, or .json).

        """
        import os  # Moved inside the function

        # If the input is a dictionary, process it as JSON
        if isinstance(record_filename_or_object, dict):
            result = self.import_from_json(record_filename_or_object)
        else:
            # Determine file extension
            file_extension = os.path.splitext(record_filename_or_object)[1].lower()

            if file_extension == ".csv":
                result = self.import_from_csv(record_filename_or_object, delimiter=",")
            elif file_extension == ".tsv":
                result = self.import_from_csv(record_filename_or_object, delimiter="\t")
            elif file_extension == ".json":
                result = self.import_from_json(record_filename_or_object)
            else:
                raise ValueError("Unsupported file type. Please provide a CSV, TSV, or JSON file.")

        return result

    #the json object can be a filename string or can be json object which is actually a dictionary.
    def import_from_json(self, json_filename_or_object):
        """
        Imports a fig_dict from a JSON-formatted string, file path, or dictionary.
            - If a string is passed, the method attempts to parse it as a JSON-formatted string.
            - If parsing fails, it attempts to treat the string as a file path to a JSON file.
            - If the file isn’t found, it appends ".json" and tries again.
            - If a dictionary is passed, it is directly assigned to fig_dict.
            - Includes detailed error feedback if JSON parsing fails, highlighting common issues like 
              improper quote usage or malformed booleans.

        Args:
            json_filename_or_object (str or dict): A JSON string, a path to a .json file, or a dict
                representing a valid fig_dict structure.

        Returns:
            dict: The parsed and loaded fig_dict.

        """
        if type(json_filename_or_object) == type(""): #assume it's a json_string or filename_and_path.
            try:
                record = json.loads(json_filename_or_object) #first check if it's a json string.
            except json.JSONDecodeError as e1:  # Catch specific exception
                try:
                    import os
                    #if the filename does not exist, check if adding ".json" fixes the problem.
                    if not os.path.exists(json_filename_or_object):
                        json_added_filename = json_filename_or_object + ".json"
                        if os.path.exists(json_added_filename): json_filename_or_object = json_added_filename #only change the filename if the json_filename exists.
                    # Open the file in read mode with UTF-8 encoding
                    with open(json_filename_or_object, "r", encoding="utf-8") as file:
                        # Read the entire content of the file
                        record = file.read().strip()  # Stripping leading/trailing whitespace
                        self.fig_dict = json.loads(record)
                        return self.fig_dict
                except json.JSONDecodeError as e2:  # Catch specific exception
                    print(f"JSON loading failed on record: {record}. Error: {e1} when trying to parse as a json directly, and {e2} when trying to use as a filename. You may want to try opening your JSON file in VS Code or in an online JSON Validator. Does your json have double quotes around strings? Single quotes around strings is allowed in python, but disallowed in JSON specifications. You may also need to check how Booleans and other aspects are defined in JSON.")  # Improved error reporting
        else:
            self.fig_dict = json_filename_or_object
            return self.fig_dict

    def import_from_csv(self, filename, delimiter=","):
            """
            Imports a CSV or TSV file and converts its contents into a fig_dict.
                - The input file must follow a specific format, as of 6/25/25, but this may be made more general in the future.
                    * Lines 1–5 define config metadata (e.g., comments, datatype, axis labels).
                    * Line 6 defines series names.
                    * Data rows begin on line 9.
                    * The data table portion of the file can be xyxy or xyyy data.

            Args:
                filename (str): File path to the CSV or TSV file. If no extension is provided,
                    ".csv" or ".tsv" is inferred based on the delimiter.
                delimiter (str, optional): Field separator character. Defaults to ",". Use "\\t" for TSV files.

            Returns:
                dict: The created fig_dict.

            """
            import os
            import math

            # Ensure correct file extension
            file_extension = os.path.splitext(filename)[1]
            if delimiter == "," and not file_extension: #for no extension present.
                filename += ".csv"
            elif delimiter == "\t" and not file_extension:  #for no extension present.
                filename += ".tsv"

            with open(filename, "r", encoding="utf-8") as file:
                file_content = file.read().strip()

            arr = file_content.split("\n") #separate the rows.
            if len(arr[-1].strip()) < 2:
                arr = arr[:-1]  # Trim empty trailing line

            # Extract metadata
            comments = arr[0].split(delimiter)[0].split(":")[1].strip()
            datatype = arr[1].split(delimiter)[0].split(":")[1].strip()
            chart_label = arr[2].split(delimiter)[0].split(":")[1].strip()
            x_label = arr[3].split(delimiter)[0].split(":")[1].strip()
            y_label = arr[4].split(delimiter)[0].split(":")[1].strip()
            series_names_array = [
                n.strip() for n in arr[5].split(":")[1].split('"')[0].split(delimiter)
                if n.strip()
            ]

            raw_data = [row.split(delimiter) for row in arr[8:]]
            column_count = len(raw_data[0])
            
            # Format detection
            series_columns_format = "xyyy"  # assume xyyy as default
            if column_count >= 4:
                last_row = raw_data[-1]
                for i in range(1, column_count, 2):
                    # Get last row, with failsafe that handles rows that may 
                    # have missing delimiters or fewer columns than expected
                    val = last_row[i] if i < len(last_row) else ""
                    try:
                        num = float(val)
                        if math.isnan(num):
                            series_columns_format = "xyxy"
                            break
                    except (ValueError, TypeError):
                        series_columns_format = "xyxy"
                        break

            # Prepare fig_dict
            self.fig_dict["comments"] = comments
            self.fig_dict["datatype"] = datatype
            self.fig_dict["layout"]["title"] = {"text": chart_label}
            self.fig_dict["layout"]["xaxis"]["title"] = {"text": x_label}
            self.fig_dict["layout"]["yaxis"]["title"] = {"text": y_label}

            #Create the series data sets.
            new_data = []

            if series_columns_format == "xyyy":
                parsed_data = [[float(val) if val.strip() else None for val in row] for row in raw_data]
                for i in range(1, column_count):
                    x_series = [row[0] for row in parsed_data if row[0] is not None]
                    y_series = [row[i] for row in parsed_data if row[i] is not None]
                    data_series_dict = {
                        "name": series_names_array[i - 1] if i - 1 < len(series_names_array) else f"Series {i}",
                        "x": x_series,
                        "y": y_series,
                        "uid": str(i - 1)
                    }
                    new_data.append(data_series_dict)
            else:  # xyxy format
                for i in range(0, column_count, 2):
                    x_vals = []
                    y_vals = []
                    for row in raw_data:
                        try:
                            x = float(row[i])
                            y = float(row[i + 1])
                            x_vals.append(x)
                            y_vals.append(y)
                        except (ValueError, IndexError):
                            continue
                    series_number = i // 2
                    data_series_dict = {
                        "name": series_names_array[series_number] if series_number < len(series_names_array) else f"Series {series_number + 1}",
                        "x": x_vals,
                        "y": y_vals,
                        "uid": str(series_number)
                    }
                    new_data.append(data_series_dict)
            self.fig_dict["data"] = new_data
            return self.fig_dict

    def export_to_csv(self, filename=None, delimiter=",", 
                      update_and_validate=True, validate=True, 
                      simulate_all_series=True, remove_simulate_fields=False, 
                      remove_equation_fields=False, remove_remaining_hints=False):
        """
        Serializes fig_dict into a CSV file with optional preprocessing.
        Returns the modified fig_dict like export_to_json_file.

        Args:
            filename (str, optional): Destination filename. Appends '.csv' if missing.
            delimiter (str): Field separator. Defaults to ','.
            update_and_validate (bool): Apply corrections before validation.
            validate (bool): Perform validation without corrections.
            simulate_all_series (bool): Simulate any series with simulate fields.
            remove_simulate_fields (bool): Remove 'simulate' fields if True.
            remove_equation_fields (bool): Remove 'equation' fields if True.
            remove_remaining_hints (bool): Remove developer hints if True.

        Returns:
            dict: The fig_dict after processing.
        """
        import copy
        original_fig_dict = copy.deepcopy(self.fig_dict)

        if simulate_all_series:
            self.fig_dict = simulate_as_needed_in_fig_dict(self.fig_dict)
        if remove_simulate_fields:
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['simulate'])
        if remove_equation_fields:
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['equation'])
        if remove_remaining_hints:
            self.remove_hints()
        if update_and_validate:
            self.update_and_validate_JSONGrapher_record()
        elif validate:
            self.validate_JSONGrapher_record()

        fig_dict = self.fig_dict
        comments    = fig_dict.get("comments", "")
        datatype    = fig_dict.get("datatype", "")
        graph_title = fig_dict.get("layout", {}).get("title", {}).get("text", "")
        x_label     = fig_dict.get("layout", {}).get("xaxis", {}).get("title", {}).get("text", "")
        y_label     = fig_dict.get("layout", {}).get("yaxis", {}).get("title", {}).get("text", "")
        data_sets   = fig_dict.get("data", [])

        series_names = delimiter.join(ds.get("name", "") for ds in data_sets)

        lines = [
            f"comments: {comments}",
            f"datatype: {datatype}",
            f"graph_title: {graph_title}",
            f"x_label: {x_label}",
            f"y_label: {y_label}",
            f"series_names:{delimiter}{series_names}"
        ]

        all_x = [ds.get("x", []) for ds in data_sets]
        is_xyyy = bool(all_x) and all(x == all_x[0] for x in all_x)

        if is_xyyy:
            y_headers = [f"y_{i+1}" for i in range(len(data_sets))]
            lines.append(delimiter.join(["x_values"] + y_headers))
            for i in range(len(all_x[0])):
                row = [str(all_x[0][i])]
                for ds in data_sets:
                    y_vals = ds.get("y", [])
                    row.append(str(y_vals[i]) if i < len(y_vals) else "")
                lines.append(delimiter.join(row))
        else:
            headers = [f"x_{i+1}{delimiter}y_{i+1}" for i in range(len(data_sets))]
            lines.append(delimiter.join(headers))
            max_len = max((len(ds.get("x", [])) for ds in data_sets), default=0)
            for i in range(max_len):
                row_cells = []
                for ds in data_sets:
                    x_vals = ds.get("x", [])
                    y_vals = ds.get("y", [])
                    xv = str(x_vals[i]) if i < len(x_vals) else ""
                    yv = str(y_vals[i]) if i < len(y_vals) else ""
                    row_cells.extend([xv, yv])
                lines.append(delimiter.join(row_cells))

        csv_string = "\r\n".join(lines) + "\r\n"
        out_filename = filename if filename else "mergedJSONGrapherRecord.csv"

        if len(out_filename) > 0:
            if '.csv' not in out_filename.lower():
                out_filename += ".csv"
            with open(out_filename, 'w', encoding='utf-8') as f:
                f.write(csv_string)

        modified_fig_dict = self.fig_dict
        self.fig_dict = original_fig_dict
        return modified_fig_dict


    def set_datatype(self, datatype):
        """
        Sets the 'datatype' field within the fig_dict. Used to classify the record, for example by experiment type, and may 
        point to a schema. May be a url.       

        Expected to be a string with no spaces, and may be a url. Underscore 
        may be included "_" and double underscore "__" has a special meaning.
        See manual for information about the use of double underscore.

        Args:
            datatype (str): The new string to use for the datatype field.

        """
        self.fig_dict['datatype'] = datatype

    def set_comments(self, comments):
        """
        Updates the 'comments' field in the fig_dict.

        Args:
            comments (str): Text to assign to fig_dict["comments"].
        """
        self.fig_dict['comments'] = comments

    def set_graph_title(self, graph_title):
        """
        Sets the main title of the graph. Updates the title field in the fig_dict's layout section.

        Args:
            graph_title (str): The title text to assign to fig_dict["layout"]["title"]["text"].
        """
        self.fig_dict['layout']['title']['text'] = graph_title

    def set_x_axis_label_including_units(self, x_axis_label_including_units, remove_plural_units=True):
        """
        Sets and validates the axis label in the fig_dict's layout, with optional removal of plural 's' in units.
            - Utilizes validate_JSONGrapher_axis_label to enforce proper label formatting and unit conventions.
            - Ensures the layout["xaxis"] structure is initialized safely before assignment.
            - The layout_style structure is safely initialized if missing.

        Args:
            x_axis_label_including_units (str): The full axis label text, including units in parentheses (e.g., "Time (s)").
            remove_plural_units (bool): If True (default), converts plural unit terms to singular during validation.

        """
        if "xaxis" not in self.fig_dict['layout'] or not isinstance(self.fig_dict['layout'].get("xaxis"), dict):
            self.fig_dict['layout']["xaxis"] = {}  # Initialize x-axis as a dictionary if it doesn't exist.
        _validation_result, _warnings_list, x_axis_label_including_units = validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=remove_plural_units)
        #setdefault avoids problems for missing fields.
        self.fig_dict.setdefault("layout", {}).setdefault("xaxis", {}).setdefault("title", {})["text"] = x_axis_label_including_units 

    def set_y_axis_label_including_units(self, y_axis_label_including_units, remove_plural_units=True):
        """
        Sets and validates the axis label in the fig_dict's layout, with optional removal of plural 's' in units.
            - Utilizes validate_JSONGrapher_axis_label to enforce proper label formatting and unit conventions.
            - Ensures the layout["yaxis"] structure is initialized safely before assignment.
            - The layout_style structure is safely initialized if missing.

        Args:
            y_axis_label_including_units (str): The full axis label text, including units in parentheses (e.g., "Time (s)").
            remove_plural_units (bool): If True (default), converts plural unit terms to singular during validation.

        """
        if "yaxis" not in self.fig_dict['layout'] or not isinstance(self.fig_dict['layout'].get("yaxis"), dict):
            self.fig_dict['layout']["yaxis"] = {}  # Initialize y-axis as a dictionary if it doesn't exist.       
        _validation_result, _warnings_list, y_axis_label_including_units = validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=remove_plural_units)
        #setdefault avoids problems for missing fields.
        self.fig_dict.setdefault("layout", {}).setdefault("yaxis", {}).setdefault("title", {})["text"] = y_axis_label_including_units

    def set_z_axis_label_including_units(self, z_axis_label_including_units, remove_plural_units=True):
        """
        Sets and validates the axis label in the fig_dict's layout, with optional removal of plural 's' in units.
            - Utilizes validate_JSONGrapher_axis_label to enforce proper label formatting and unit conventions.
            - Ensures the layout["zaxis"] structure is initialized safely before assignment.
            - The layout_style structure is safely initialized if missing.

        Args:
            z_axis_label_including_units (str): The full axis label text, including units in parentheses (e.g., "Time (s)").
            remove_plural_units (bool): If True (default), converts plural unit terms to singular during validation.

        """
        if "zaxis" not in self.fig_dict['layout'] or not isinstance(self.fig_dict['layout'].get("zaxis"), dict):
            self.fig_dict['layout']["zaxis"] = {}  # Initialize y-axis as a dictionary if it doesn't exist.
            self.fig_dict['layout']["zaxis"]["title"] = {}  # Initialize y-axis as a dictionary if it doesn't exist.
        _validation_result, _warnings_list, z_axis_label_including_units = validate_JSONGrapher_axis_label(z_axis_label_including_units, axis_name="z", remove_plural_units=remove_plural_units)
        #setdefault avoids problems for missing fields.
        self.fig_dict.setdefault("layout", {}).setdefault("zaxis", {}).setdefault("title", {})["text"] = z_axis_label_including_units

    #function to set the min and max of the x axis in plotly way.
    def set_x_axis_range(self, min_value, max_value):
        """
        Sets the minimum and maximum range for the axis in the fig_dict's layout.

        Args:
            min_value (float): Lower limit of the axis range.
            max_value (float): Upper limit of the axis range.

        """
        self.fig_dict["layout"]["xaxis"][0] = min_value
        self.fig_dict["layout"]["xaxis"][1] = max_value

    #function to set the min and max of the y axis in plotly way.
    def set_y_axis_range(self, min_value, max_value):
        """
        Sets the minimum and maximum range for the axis in the fig_dict's layout.

        Args:
            min_value (float): Lower limit of the axis range.
            max_value (float): Upper limit of the axis range.

        """
        self.fig_dict["layout"]["yaxis"][0] = min_value
        self.fig_dict["layout"]["yaxis"][1] = max_value

        #function to set the min and max of the y axis in plotly way.

    def set_z_axis_range(self, min_value, max_value):
        """
        Sets the minimum and maximum range for the axis in the fig_dict's layout.

        Args:
            min_value (float): Lower limit of the axis range.
            max_value (float): Upper limit of the axis range.

        """
        self.fig_dict["layout"]["zaxis"][0] = min_value
        self.fig_dict["layout"]["zaxis"][1] = max_value

    #function to scale the values in the data series by arbitrary amounts.
    def scale_record(self, num_to_scale_x_values_by = 1, num_to_scale_y_values_by = 1):
        """
        Scales all x and y values across data series in the fig_dict by specified scalar factors.
            - Modifies fig_dict in-place by replacing it with the scaled version.

        Args:
            num_to_scale_x_values_by (float): Scaling factor applied to all x-values. Default is 1 (no change).
            num_to_scale_y_values_by (float): Scaling factor applied to all y-values. Default is 1 (no change).

        """
        self.fig_dict = scale_fig_dict_values(self.fig_dict, num_to_scale_x_values_by=num_to_scale_x_values_by, num_to_scale_y_values_by=num_to_scale_y_values_by)

    def set_layout_fields(self, comments="", graph_title="", x_axis_label_including_units="", y_axis_label_including_units="", x_axis_comments="",y_axis_comments="", remove_plural_units=True):
        """
        Scales all x and y values across data series in the fig_dict by specified scalar factors.
            - Modifies fig_dict in-place by replacing it with the scaled version.

        Args:
            num_to_scale_x_values_by (float): Scaling factor applied to all x-values. Default is 1 (no change).
            num_to_scale_y_values_by (float): Scaling factor applied to all y-values. Default is 1 (no change).
        """
        # comments: General comments about the layout. Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        # graph_title: Title of the graph.
        # xaxis_title: Title of the x-axis, including units.
        # xaxis_comments: Comments related to the x-axis.  Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        # yaxis_title: Title of the y-axis, including units.
        # yaxis_comments: Comments related to the y-axis.  Allowed by JSONGrapher, but will be removed if converted to a plotly object.
        
        _validation_result, _warnings_list, x_axis_label_including_units = validate_JSONGrapher_axis_label(x_axis_label_including_units, axis_name="x", remove_plural_units=remove_plural_units)              
        _validation_result, _warnings_list, y_axis_label_including_units = validate_JSONGrapher_axis_label(y_axis_label_including_units, axis_name="y", remove_plural_units=remove_plural_units)
        self.fig_dict['layout']["title"]['text'] = graph_title
        self.fig_dict['layout']["xaxis"]["title"]['text'] = x_axis_label_including_units
        self.fig_dict['layout']["yaxis"]["title"]['text'] = y_axis_label_including_units
        
        #populate any optional fields, if provided:
        if len(comments) > 0:
            self.fig_dict['layout']["comments"] = comments
        if len(x_axis_comments) > 0:
            self.fig_dict['layout']["xaxis"]["comments"] = x_axis_comments
        if len(y_axis_comments) > 0:
            self.fig_dict['layout']["yaxis"]["comments"] = y_axis_comments     
        return self.fig_dict['layout']
    
    #This function validates the output before exporting, and also has an option of removing hints.
    #The update_and_validate function will clean for plotly.
    #simulate all series will simulate any series as needed.
    #TODO: need to add an "include_formatting" option
    def export_to_json_file(self, filename, update_and_validate=True, validate=True, simulate_all_series = True, remove_simulate_fields= False, remove_equation_fields= False, remove_remaining_hints=False):
        """
        Exports the current fig_dict to a JSON file with optional simulation, cleaning, and validation.
            - Ensures compatibility with Plotly and external tools by validating and cleaning metadata.
            - JSON file is saved using UTF-8 encoding with 4-space indentation.

        Args:
            filename (str): Destination filename. A '.json' extension will be appended if missing.
            update_and_validate (bool): If True (default), applies automatic corrections and cleans the fig_dict before export.
            validate (bool): If True (default), performs validation even without updates.
            simulate_all_series (bool): If True (default), evaluates all data series containing a 'simulate' field prior to export.
            remove_simulate_fields (bool): If True, strips out 'simulate' fields from each data series before export.
            remove_equation_fields (bool): If True, removes 'equation' fields from each series.
            remove_remaining_hints (bool): If True, deletes developer hints from the record for cleaner output.

        Returns:
            dict: The fig_dict after all specified operations.

        """
        import copy
        original_fig_dict = copy.deepcopy(self.fig_dict)
        #if simulate_all_series is true, we'll try to simulate any series that need it, then clean the simulate fields out if requested.
        if simulate_all_series == True:
            self.fig_dict = simulate_as_needed_in_fig_dict(self.fig_dict)
        if remove_simulate_fields == True:
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['simulate'])
        if remove_equation_fields == True:
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['equation'])
        if remove_remaining_hints == True:
            self.remove_hints()
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
        elif validate: #this will validate without doing automatic updates.
            self.validate_JSONGrapher_record()

        # filename with path to save the JSON file.       
        if len(filename) > 0: #this means we will be writing to file.
            # Check if the filename has an extension and append `.json` if not
            if '.json' not in filename.lower():
                filename += ".json"
            #Write to file using UTF-8 encoding.
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.fig_dict, f, indent=4)
        modified_fig_dict = self.fig_dict #store the modified fig_dict for return .
        self.fig_dict = original_fig_dict #restore the original fig_dict.
        return modified_fig_dict

    def get_plotly_json(self, plot_style = None, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True,adjust_implicit_data_ranges=True):
        """
        Generates a Plotly-compatible JSON from the current fig_dict
            - Relies on get_plotly_fig() for figure construction and formatting.

        Args:
            plot_style (dict, optional): plot_style to apply before exporting.
            update_and_validate (bool): If True (default), cleans and validates the figure before export.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            evaluate_all_equations (bool): If True (default), computes outputs for any equation-based series before exporting.
            adjust_implicit_data_ranges (bool): If True (default), automatically adjusts 'equation' and 'simulate' series axis ranges to the data, for cases that are compatible with that feature.

        Returns:
            dict: The Plotly-compatible JSON object, a dictionary, which can be directly plotted with plotly.

        """
        fig = self.get_plotly_fig(plot_style=plot_style,
                                  update_and_validate=update_and_validate, 
                                  simulate_all_series=simulate_all_series, 
                                  evaluate_all_equations=evaluate_all_equations, 
                                  adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        plotly_json_string = fig.to_plotly_json()
        return plotly_json_string

    def export_plotly_json(self, filename, plot_style = None, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True,adjust_implicit_data_ranges=True):
        """
        Generates a Plotly-compatible JSON file from the current fig_dict and exports it to disk.
            - Relies on get_plotly_fig() for figure construction and formatting.
            - Exports the result to a UTF-8 encoded file using standard JSON formatting.

        Args:
            filename (str): Path for the output file. If no ".json" extension is present, it will be added.
            plot_style (dict, optional): plot_style to apply before exporting.
            update_and_validate (bool): If True (default), cleans and validates the figure before export.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            evaluate_all_equations (bool): If True (default), computes outputs for any equation-based series before exporting.
            adjust_implicit_data_ranges (bool): If True (default), automatically adjusts 'equation' and 'simulate' series axis ranges to the data, for cases that are compatible with that feature.

        Returns:
            dict: The Plotly-compatible JSON object, a dictionary, which can be directly plotted with plotly.

        """
        plotly_json_string = self.get_plotly_json(plot_style=plot_style, update_and_validate=update_and_validate, simulate_all_series=simulate_all_series, evaluate_all_equations=evaluate_all_equations, adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        if len(filename) > 0: #this means we will be writing to file.
            # Check if the filename has an extension and append `.json` if not
            if '.json' not in filename.lower():
                filename += ".json"
            #Write to file using UTF-8 encoding.
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(plotly_json_string, f, indent=4)
        return plotly_json_string

    #simulate all series will simulate any series as needed.
    def get_plotly_fig(self, plot_style=None, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True, adjust_offset2d=True, adjust_arrange2dTo3d=True):
        """
        Constructs and returns a Plotly figure object based on the current fig_dict with optional preprocessing steps.
            - A deep copy of fig_dict is created to avoid unintended mutation of the source object.
            - Applies plot styles before cleaning and validation.
            - Removes JSONGrapher specific fields (e.g., 'simulate', 'equation') before handing off to Plotly.

        Args:
            plot_style (str, dict, or list): plot_style dictionary. Use '' to skip styling and 'none' to clear all styles.
              Also accepts other options:
                - A dictionary with layout_style and trace_styles_collection (normal case).
                - A string such as 'default' to use for both layout_style and trace_styles_collection name
                - A list of length two with layout_style and trace_styles_collection name
            update_and_validate (bool): If True (default), applies automated corrections and validation.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            evaluate_all_equations (bool): If True (default), computes outputs for any equation-based series before exporting.
            adjust_implicit_data_ranges (bool): If True (default), automatically adjusts 'equation' and 'simulate' series axis ranges to the data, for cases that are compatible with that feature.

        Returns:
            plotly fig: A fully constructed and styled Plotly figure object.


        """
        if plot_style is None: #should not initialize mutable objects in arguments line, so doing here.
            plot_style = {"layout_style": "", "trace_styles_collection": ""}  # Fresh dictionary per function call
        
        import plotly.io as pio
        import copy
        if plot_style == {"layout_style":"", "trace_styles_collection":""}: #if the plot_style received is the default, we'll check if the fig_dict has a plot_style.
            plot_style = self.fig_dict.get("plot_style", {"layout_style":"", "trace_styles_collection":""}) #retrieve from self.fig_dict, and use default if not there.
        #This code *does not* simply modify self.fig_dict. It creates a deepcopy and then puts the final x y data back in.
        self.fig_dict = execute_implicit_data_series_operations(self.fig_dict, 
                                                                simulate_all_series=simulate_all_series, 
                                                                evaluate_all_equations=evaluate_all_equations, 
                                                                adjust_implicit_data_ranges=adjust_implicit_data_ranges,
                                                                adjust_offset2d = False,
                                                                adjust_arrange2dTo3d=False)
        #Regardless of implicit data series, we make a fig_dict copy, because we will clean self.fig_dict for creating the new plotting fig object.
        original_fig_dict = copy.deepcopy(self.fig_dict) 
        #The adjust_offset2d should be on the copy, if requested.
        self.fig_dict = execute_implicit_data_series_operations(self.fig_dict, 
                                                                simulate_all_series=False, 
                                                                evaluate_all_equations=False, 
                                                                adjust_implicit_data_ranges=False,
                                                                adjust_offset2d=adjust_offset2d,
                                                                adjust_arrange2dTo3d=adjust_arrange2dTo3d)
        #before cleaning and validating, we'll apply styles.
        plot_style = parse_plot_style(plot_style=plot_style)
        self.apply_plot_style(plot_style=plot_style)
        #Now we clean out the fields and make a plotly object.
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record(clean_for_plotly=False) #We use the False argument here because the cleaning will be on the next line with beyond default arguments.
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['simulate', 'custom_units_chevrons', 'equation', 'trace_style', '3d_axes', 'bubble', 'superscripts', 'nested_comments', 'extraInformation'])
        fig = pio.from_json(json.dumps(self.fig_dict))
        #restore the original fig_dict.
        self.fig_dict = original_fig_dict 
        return fig

    #Just a wrapper aroudn plot_with_plotly.
    def plot(self, plot_style = None, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True):
        """
        Plots the current fig_dict using Plotly with optional preprocessing, simulation, and visual styling.
            - Acts as a convenience wrapper around plot_with_plotly().
            
        Args:
            plot_style (str, dict, or list): plot_style dictionary. Use '' to skip styling and 'none' to clear all styles.
              Also accepts other options:
                - A dictionary with layout_style and trace_styles_collection (normal case).
                - A string such as 'default' to use for both layout_style and trace_styles_collection name
                - A list of length two with layout_style and trace_styles_collection name
            update_and_validate (bool): If True (default), applies automated corrections and validation.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            evaluate_all_equations (bool): If True (default), computes outputs for any equation-based series before exporting.
            adjust_implicit_data_ranges (bool): If True (default), automatically adjusts 'equation' and 'simulate' series axis ranges to the data, for cases that are compatible with that feature.

        Returns:
            plotly fig: A Plotly figure object rendered from the processed fig_dict. However, the main 'real' return is a graph window that pops up.

        """
        if plot_style is None: #should not initialize mutable objects in arguments line, so doing here.
            plot_style = {"layout_style": "", "trace_styles_collection": ""}  # Fresh dictionary per function call
        return self.plot_with_plotly(plot_style=plot_style, update_and_validate=update_and_validate, simulate_all_series=simulate_all_series, evaluate_all_equations=evaluate_all_equations, adjust_implicit_data_ranges=adjust_implicit_data_ranges)

    #simulate all series will simulate any series as needed. If changing this function's arguments, also change those for self.plot()
    def plot_with_plotly(self, plot_style = None, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True, browser=True):
        """
        Displays the current fig_dict as an interactive Plotly figure with optional preprocessing and styling.
        A Plotly figure object rendered from the processed fig_dict. However, the main 'real' return is a graph window that pops up.
            - Wraps get_plotly_fig() and renders the resulting figure using fig.show().
            - Safely leaves the internal fig_dict unchanged after rendering.
        
        Args:
            plot_style (str, dict, or list): plot_style dictionary. Use '' to skip styling and 'none' to clear all styles.
              Also accepts other options:
                - A dictionary with layout_style and trace_styles_collection (normal case).
                - A string such as 'default' to use for both layout_style and trace_styles_collection name
                - A list of length two with layout_style and trace_styles_collection name
            update_and_validate (bool): If True (default), applies automated corrections and validation.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            evaluate_all_equations (bool): If True (default), computes outputs for any equation-based series before exporting.
            adjust_implicit_data_ranges (bool): If True (default), automatically adjusts 'equation' and 'simulate' series axis ranges to the data, for cases that are compatible with that feature.

        Returns:
            plotly fig: A Plotly figure object rendered from the processed fig_dict. However, the main 'real' return is a graph window that pops up.

        """
        if browser == True:
            import plotly.io as pio; pio.renderers.default = "browser"#
        if plot_style is None: #should not initialize mutable objects in arguments line, so doing here.
            plot_style = {"layout_style": "", "trace_styles_collection": ""}  # Fresh dictionary per function call
        fig = self.get_plotly_fig(plot_style=plot_style,
                                  update_and_validate=update_and_validate, 
                                  simulate_all_series=simulate_all_series, 
                                  evaluate_all_equations=evaluate_all_equations, 
                                  adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        fig.show()
        return fig
        #No need for fig.close() for plotly figures.


    #simulate all series will simulate any series as needed.
    def export_to_plotly_png(self, filename, plot_style = None, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True, timeout=10):
        """
        Exports the current fig_dict as a PNG image file using a Plotly-rendered figure.
        Notes:
            - Relies on get_plotly_fig() to construct the Plotly figure.
            - Uses export_plotly_image_with_timeout() to safely render and export the image without stalling.

        Args:
            filename (str): The name of the output PNG file. If missing an extension, ".png" will be inferred downstream.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            update_and_validate (bool): If True (default), performs automated cleanup and validation before rendering.
            timeout (int): Max number of seconds allotted to render and export the figure.

        """
        fig = self.get_plotly_fig(plot_style=plot_style,
                                  update_and_validate=update_and_validate, 
                                  simulate_all_series=simulate_all_series, 
                                  evaluate_all_equations=evaluate_all_equations, 
                                  adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        # Save the figure to a file, but use the timeout version.
        self.export_plotly_image_with_timeout(plotly_fig = fig, filename=filename, timeout=timeout)

    def export_plotly_image_with_timeout(self, plotly_fig, filename, timeout=10):
        """
        Attempts to export a Plotly figure to a PNG file using Kaleido, with timeout protection.
            - Runs the export in a background daemon thread to ensure timeout safety.
            - MathJax is disabled to improve speed and compatibility.
            - If export exceeds the timeout, a warning is printed and no file is saved.
            - Kaleido must be installed and working; if issues persist, consider using `export_to_matplotlib_png()` as a fallback.

        Args:
            plotly_fig (plotly.graph_objs._figure.Figure): The Plotly figure to export as an image.
            filename (str): Target PNG file name. Adds ".png" if not already present.
            timeout (int): Maximum duration (in seconds) to allow the export before timing out. Default is 10.

        """
        # Ensure filename ends with .png
        if not filename.lower().endswith(".png"):
            filename += ".png"
        import plotly.io as pio
        pio.kaleido.scope.mathjax = None
        fig = plotly_fig
        
        def export():
            try:
                fig.write_image(filename, engine="kaleido")
            except Exception as e: # This is so VS code pylint does not flag this line. pylint: disable=broad-except
                print(f"Export failed: {e}")

        import threading
        thread = threading.Thread(target=export, daemon=True)  # Daemon ensures cleanup
        thread.start()
        thread.join(timeout=timeout)  # Wait up to 10 seconds
        if thread.is_alive():
            print("Skipping Plotly png export: Operation timed out. Plotly image export often does not work from Python. Consider using export_to_matplotlib_png.")

    #update_and_validate will 'clean' for plotly. 
    #In the case of creating a matplotlib figure, this really just means removing excess fields.
    #simulate all series will simulate any series as needed.
    def get_matplotlib_fig(self, plot_style = None, update_and_validate=True, simulate_all_series = True, evaluate_all_equations = True, adjust_implicit_data_ranges=True, adjust_offset2d=True, adjust_arrange2dTo3d=True):
        """
        Constructs and returns a matplotlib figure generated from fig_dict, with optional simulation, preprocessing, and styling.

        Args:
            plot_style (str, dict, or list): plot_style dictionary. Use '' to skip styling and 'none' to clear all styles.
              Also accepts other options:
                - A dictionary with layout_style and trace_styles_collection (normal case).
                - A string such as 'default' to use for both layout_style and trace_styles_collection name
                - A list of length two with layout_style and trace_styles_collection name
            update_and_validate (bool): If True (default), applies automated corrections and validation.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            evaluate_all_equations (bool): If True (default), computes outputs for any equation-based series before exporting.
            adjust_implicit_data_ranges (bool): If True (default), automatically adjusts 'equation' and 'simulate' series axis ranges to the data, for cases that are compatible with that feature.            

        Returns:
            matplotlib fig: A matplotlib figure object based on fig_dict.
            
        """
        if plot_style is None: #should not initialize mutable objects in arguments line, so doing here.
            plot_style = {"layout_style": "", "trace_styles_collection": ""}  # Fresh dictionary per function call
        import copy
        if plot_style == {"layout_style":"", "trace_styles_collection":""}: #if the plot_style received is the default, we'll check if the fig_dict has a plot_style.
            plot_style = self.fig_dict.get("plot_style", {"layout_style":"", "trace_styles_collection":""})
        #This code *does not* simply modify self.fig_dict. It creates a deepcopy and then puts the final x y data back in.
        self.fig_dict = execute_implicit_data_series_operations(self.fig_dict, 
                                                                simulate_all_series=simulate_all_series, 
                                                                evaluate_all_equations=evaluate_all_equations, 
                                                                adjust_implicit_data_ranges=adjust_implicit_data_ranges,
                                                                adjust_offset2d = False,
                                                                adjust_arrange2dTo3d=False)
        #Regardless of implicit data series, we make a fig_dict copy, because we will clean self.fig_dict for creating the new plotting fig object.
        original_fig_dict = copy.deepcopy(self.fig_dict) 
        #The adjust_offset2d should be on the copy, if requested.
        self.fig_dict = execute_implicit_data_series_operations(self.fig_dict, 
                                                                simulate_all_series=False, 
                                                                evaluate_all_equations=False, 
                                                                adjust_implicit_data_ranges=False,
                                                                adjust_offset2d=adjust_offset2d,
                                                                adjust_arrange2dTo3d=adjust_arrange2dTo3d)
        #before cleaning and validating, we'll apply styles.
        plot_style = parse_plot_style(plot_style=plot_style)
        self.apply_plot_style(plot_style=plot_style)
        if update_and_validate == True: #this will do some automatic 'corrections' during the validation.
            self.update_and_validate_JSONGrapher_record()
            self.fig_dict = clean_json_fig_dict(self.fig_dict, fields_to_update=['simulate', 'custom_units_chevrons', 'equation', 'trace_style'])
        fig = convert_JSONGrapher_dict_to_matplotlib_fig(self.fig_dict)
        self.fig_dict = original_fig_dict #restore the original fig_dict.
        return fig

    #simulate all series will simulate any series as needed.
    def plot_with_matplotlib(self, plot_style=None, update_and_validate=True, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True):
        """
        Displays the current fig_dict as a matplotlib figure with optional preprocessing and simulation.

        Args:
            update_and_validate (bool): If True (default), applies automated corrections and validation.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            evaluate_all_equations (bool): If True (default), computes outputs for any equation-based series before exporting.
            adjust_implicit_data_ranges (bool): If True (default), automatically adjusts 'equation' and 'simulate' series axis ranges to the data, for cases that are compatible with that feature.            

        """
        import matplotlib.pyplot as plt
        fig = self.get_matplotlib_fig(plot_style=plot_style,
                                      update_and_validate=update_and_validate, 
                                      simulate_all_series=simulate_all_series, 
                                      evaluate_all_equations=evaluate_all_equations, 
                                      adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        plt.show()
        plt.close(fig) #remove fig from memory.

    #simulate all series will simulate any series as needed.
    def export_to_matplotlib_png(self, filename, plot_style = None, update_and_validate=True, simulate_all_series = True, evaluate_all_equations = True, adjust_implicit_data_ranges=True):
        """
        Export the current fig_dict as a PNG image by rendering it with matplotlib.
            - Calls get_matplotlib_fig() to generate the figure.
            - Saves the image using matplotlib's savefig().
            - Automatically closes the figure after saving to free memory.

        Args:
            filename (str): Output filepath for the image. Adds a ".png" extension if not provided.
            simulate_all_series (bool): If True (default), simulates any data series that include a 'simulate' field before exporting.
            update_and_validate (bool): If True (default), performs cleanup and validation before rendering.

        """
        import matplotlib.pyplot as plt
        # Ensure filename ends with .png
        if not filename.lower().endswith(".png"):
            filename += ".png"
        fig = self.get_matplotlib_fig(plot_style=plot_style,
                                      update_and_validate=update_and_validate, 
                                      simulate_all_series=simulate_all_series, 
                                      evaluate_all_equations=evaluate_all_equations, 
                                      adjust_implicit_data_ranges=adjust_implicit_data_ranges)
        # Save the figure to a file
        fig.savefig(filename)
        plt.close(fig) #remove fig from memory.

    def add_hints(self):
        """
        Populate empty fields in fig_dict with placeholder text from hints_dictionary.
            - Each key in hints_dictionary represents a dotted path (e.g., "['layout']['xaxis']['title']") pointing to a location within fig_dict.
            - If the specified field is missing or contains an empty string, the corresponding hint is
        Though there is no actual return, there is an implied return of self.fig_dict being modfied.
            
        """
        for hint_key, hint_text in self.hints_dictionary.items():
            # Parse the hint_key into a list of keys representing the path in the record.
            # For example, if hint_key is "['layout']['xaxis']['title']",
            # then record_path_as_list will be ['layout', 'xaxis', 'title'].
            record_path_as_list = hint_key.strip("[]").replace("'", "").split("][")
            record_path_length = len(record_path_as_list)
            # Start at the top-level record dictionary.
            current_field = self.fig_dict

            # Loop over each key in the path.
            # For example, with record_path_as_list = ['layout', 'xaxis', 'title']:
            #    at nesting_level 0, current_path_key will be "layout";
            #    at nesting_level 1, current_path_key will be "xaxis";  <-- (this is the "xaxis" example)
            #    at nesting_level 2, current_path_key will be "title".
            # Enumerate over keys starting with index 1.
            for nesting_level, current_path_key in enumerate(record_path_as_list, start=1):
                # If not the final depth key, then retrieve from deeper.
                if nesting_level != record_path_length:
                    current_field = current_field.setdefault(current_path_key, {}) # `setdefault` will fill with the second argument if the requested field does not exist.
                else:
                    # Final key: if the field is empty, set it to hint_text.
                    if current_field.get(current_path_key, "") == "": # `get` will return the second argument if the requested field does not exist.
                        current_field[current_path_key] = hint_text
                        
    def remove_hints(self):
        """
        Remove placeholder hint text from fig_dict 
        
        Does so by checking where fields match entries in hints_dictionary.
            - Each key in hints_dictionary represents a dotted path (e.g., "['layout']['xaxis']['title']") pointing to a location within fig_dict.
            - If a matching field is found and its value equals the hint text, it is cleared to an empty string.
            - Traverses nested dictionaries safely using get() to avoid key errors.
            - Complements add_hints() by cleaning up unused or placeholder entries.
            
        """
        for hint_key, hint_text in self.hints_dictionary.items():
            # Parse the hint_key into a list of keys representing the path in the record.
            # For example, if hint_key is "['layout']['xaxis']['title']",
            # then record_path_as_list will be ['layout', 'xaxis', 'title'].
            record_path_as_list = hint_key.strip("[]").replace("'", "").split("][")
            record_path_length = len(record_path_as_list)
            # Start at the top-level record dictionary.
            current_field = self.fig_dict

            # Loop over each key in the path.
            # For example, with record_path_as_list = ['layout', 'xaxis', 'title']:
            #    at nesting_level 0, current_path_key will be "layout";
            #    at nesting_level 1, current_path_key will be "xaxis";  <-- (this is the "xaxis" example)
            #    at nesting_level 2, current_path_key will be "title".  
            # Enumerate with a starting index of 1.
            for nesting_level, current_path_key in enumerate(record_path_as_list, start=1):
                # If not the final depth key, then retrieve from deeper.
                if nesting_level != record_path_length: 
                    current_field = current_field.get(current_path_key, {})  # `get` will return the second argument if the requested field does not exist.
                else:
                    # Final key: if the field's value equals the hint text, reset it to an empty string.
                    if current_field.get(current_path_key, "") == hint_text:
                        current_field[current_path_key] = ""

    ## Start of section of JSONGRapher class functions related to styles ##

    def apply_plot_style(self, plot_style= None): 
        """
        Apply layout and trace styling configuration to fig_dict and store it in the 'plot_style' field.
            - Modifies fig_dict in place using apply_plot_style_to_plotly_dict().

        Args:
            plot_style (str, dict, or list): A style identifier. Can be a string keyword, a dictionary with 'layout_style' and
                                             'trace_styles_collection', or a list containing both. If None, defaults to an empty style dictionary.

        """
        
        #the plot_style can be a string, or a plot_style dictionary {"layout_style":"default", "trace_styles_collection":"default"} or a list of length two with those two items.
        #The plot_style dictionary can include a pair of dictionaries.
        #if apply style is called directly, we will first put the plot_style into the plot_style field
        #This way, the style will stay.
        if plot_style is None: #should not initialize mutable objects in arguments line, so doing here.
            plot_style = {"layout_style": "", "trace_styles_collection": ""}  # Fresh dictionary per function call
        self.fig_dict['plot_style'] = plot_style
        self.fig_dict = apply_plot_style_to_plotly_dict(self.fig_dict, plot_style=plot_style)
        
    def remove_plot_style(self):
        """
        Remove styling information from fig_dict, including the 'plot_style' field and associated formatting.
            - Calls remove_plot_style_from_fig_dict to strip trace_style and layout_style formatting.
        """
        self.fig_dict.pop("plot_style") #This line removes the field of plot_style from the fig_dict.
        self.fig_dict = remove_plot_style_from_fig_dict(self.fig_dict) #This line removes the actual formatting from the fig_dict.

    def set_layout_style(self, layout_style):
        """
        Set the 'layout_style' field inside fig_dict['plot_style'].
            - Initializes fig_dict["plot_style"] if it does not already exist.

        Args:
            layout_style (str or dict): A string or dictionary representing the desired layout_style.
        """
        if "plot_style" not in self.fig_dict: #create it not present.
            self.fig_dict["plot_style"] = {}  # Initialize if missing
        self.fig_dict["plot_style"]["layout_style"] = layout_style

    def remove_layout_style_setting(self):
        """
        Remove the 'layout_style' entry from fig_dict['plot_style'], if present.
        """
        if "layout_style" in self.fig_dict["plot_style"]:
            self.fig_dict["plot_style"].pop("layout_style")
            
    def extract_layout_style(self):
        """
        Extract the layout_style from fig_dict using a helper function.
            - Calls extract_layout_style_from_fig_dict to retrieve layout style information.

        Returns:
            str or dict: The extracted layout style, depending on how styles are stored.
        """
        layout_style = extract_layout_style_from_fig_dict(self.fig_dict)
        return layout_style
        
    def apply_trace_style_by_index(self, data_series_index, trace_styles_collection='', trace_style=''):
        """
        Apply a trace_style to that data_series at a specified index in the fig_dict.
            - Initializes fig_dict["plot_style"] if missing and defaults to embedded styling when needed.

        Args:
            data_series_index (int): Index of the target data series within fig_dict["data"].
            trace_styles_collection (str or dict): Optional named collection or dictionary of trace styles. Checks fig_dict["plot_style"]["trace_styles_collection"] if empty.
            trace_style (str or dict): The trace_style to apply. Can be a string for a trace_style name to be retrieved from a trace_styles_collection or can be at trace_style dictionary.

        Returns:
            dict: The updated data_series dictionary with the applied trace_style.

        """
        if trace_styles_collection == '':
            self.fig_dict.setdefault("plot_style",{}) #create the plot_style dictionary if it's not there. Else, return current value.
            trace_styles_collection = self.fig_dict["plot_style"].get("trace_styles_collection", '') #check if there is a trace_styles_collection within it, and use that. If it's not there, then use ''.
        #trace_style should be a dictionary, but can be a string.
        data_series = self.fig_dict["data"][data_series_index]
        data_series = apply_trace_style_to_single_data_series(data_series, trace_styles_collection=trace_styles_collection, trace_style_to_apply=trace_style) #this is the 'external' function, not the one in the class.
        self.fig_dict["data"][data_series_index] = data_series
        return data_series
    def set_trace_style_one_data_series(self, data_series_index, trace_style):
        """
        Sets the trace_style at the data_series with the specified index in fig_dict.
            - Overwrites any existing trace_style entry for the specified series.

        Args:
            data_series_index (int): Index of the target data series within fig_dict["data"].
            trace_style (dict or string): Dictionary or string specifying visual styling for the selected data series.

        Returns:
            dict: The updated data_series dictionary after setting the trace_style.

        """
        self.fig_dict['data'][data_series_index]["trace_style"] = trace_style
        return self.fig_dict['data'][data_series_index]
    def set_trace_styles_collection(self, trace_styles_collection):
        """
        Set the trace_styles_collection field in fig_dict['plot_style']
            - Initializes fig_dict['plot_style'] if it does not already exist.

        Args:
            trace_styles_collection (str): Name of the trace_styles_collection to apply.
        """
        self.fig_dict["plot_style"]["trace_styles_collection"] = trace_styles_collection
    def remove_trace_styles_collection_setting(self):
        """
        Remove the 'trace_styles_collection' entry from fig_dict['plot_style'], if present.
            - Deletes only the trace style setting, preserving other style-related fields like layout_style.
            - has an implied return since it modifies self.fig_dict in place.

        """
        if "trace_styles_collection" in self.fig_dict["plot_style"]:
            self.fig_dict["plot_style"].pop("trace_styles_collection")
    def set_trace_style_all_series(self, trace_style):
        """
        Set all data_series in the fig_dict to have a speicfic trace_style.

        Args:
            trace_style (dict or str): A dictionary or string naming a trace_style (e.g., 'scatter', 'spline', 'scatter_spline') defining visual properties for traces.

        """
        for data_series_index in range(len(self.fig_dict['data'])): #works with array indexing.
            self.set_trace_style_one_data_series(data_series_index, trace_style)
    def extract_trace_styles_collection(self, new_trace_styles_collection_name='', 
                                    indices_of_data_series_to_extract_styles_from=None, 
                                    new_trace_style_names_list=None, extract_colors=False):
        """
        Extract a collection of trace styles from selected data series and compile them into a named trace_styles_collection.
            - Defaults to extracting from all series in fig_dict['data'] if no indices are provided.
            - Generates indices based style names if none are supplied or found.
            - Ensures that indices and style names are aligned before processing.
            - Uses extract_trace_style_by_index to retrieve each style definition.
            
        Args:
            new_trace_styles_collection_name (str): Name to assign to the new trace_styles_collection. If empty, a placeholder is used.
            indices_of_data_series_to_extract_styles_from (list of int): Indices of the data series to extract styles from. Defaults to all series.
            new_trace_style_names_list (list of str): Names to assign to each extracted style. Auto-generated if omitted.
            extract_colors (bool): If True, includes color attributes in the extracted styles. This is typically not recommended, because a trace_style with colors would prevent automatic coloring of series across a graph.

        Returns:
            tuple:
                - str: Name of the created trace_styles_collection.
                - dict: Dictionary mapping trace_style names to their definitions.

        """
        if indices_of_data_series_to_extract_styles_from is None:  # should not initialize mutable objects in arguments line, so doing here.
            indices_of_data_series_to_extract_styles_from = []  
        if new_trace_style_names_list is None:  # should not initialize mutable objects in arguments line, so doing here.
            new_trace_style_names_list = []
        fig_dict = self.fig_dict
        new_trace_styles_collection_dictionary_without_name = {}
        if new_trace_styles_collection_name == '':
            new_trace_styles_collection_name = 'replace_this_with_your_trace_styles_collection_name'
        if indices_of_data_series_to_extract_styles_from == []:
            indices_of_data_series_to_extract_styles_from = range(len(fig_dict["data"]))
        if new_trace_style_names_list == []:
            for data_series_index in indices_of_data_series_to_extract_styles_from:
                data_series_dict = fig_dict["data"][data_series_index]
                trace_style_name = data_series_dict.get('trace_style', '')  # return blank line if not there.
                if trace_style_name == '':
                    trace_style_name = 'custom_trace_style' + str(data_series_index)
                if trace_style_name not in new_trace_style_names_list:
                    pass
                else:
                    trace_style_name = trace_style_name + str(data_series_index)
                new_trace_style_names_list.append(trace_style_name)
        if len(indices_of_data_series_to_extract_styles_from) != len(new_trace_style_names_list):
            raise ValueError("Error: The input for indices_of_data_series_to_extract_styles_from is not compatible with the input for new_trace_style_names_list. There is a difference in lengths after the automatic parsing and filling that occurs.")
        for index_to_extract_from in indices_of_data_series_to_extract_styles_from:
            new_trace_style_name = new_trace_style_names_list[index_to_extract_from]
            extracted_trace_style = extract_trace_style_by_index(fig_dict, index_to_extract_from, new_trace_style_name=new_trace_style_names_list[index_to_extract_from], extract_colors=extract_colors)
            new_trace_styles_collection_dictionary_without_name[new_trace_style_name] = extracted_trace_style[new_trace_style_name]
        return new_trace_styles_collection_name, new_trace_styles_collection_dictionary_without_name
    def export_trace_styles_collection(self, new_trace_styles_collection_name='', 
                                    indices_of_data_series_to_extract_styles_from=None, 
                                    new_trace_style_names_list=None, filename='', extract_colors=False):
        """
        Extract a set of trace styles from selected data series and write them to a trace_styles_collection file.
            - Uses extract_trace_styles_collection() to collect the styles.
            - Saves the styles to file using write_trace_styles_collection_to_file().
            
        Args:
            new_trace_styles_collection_name (str): Name of the new style collection. If empty, a placeholder name is used.
            indices_of_data_series_to_extract_styles_from (list of int): Indices of the data series to extract styles from. Defaults to all.
            new_trace_style_names_list (list of str): Names to assign to each extracted style. Auto-generated if not provided.
            filename (str): Name of the output file. If empty, the collection name is used as the filename.
            extract_colors (bool): If True, includes color attributes in the extracted styles. This is typically not recommended, because a trace_style with colors would prevent automatic coloring of series across a graph.

        Returns:
            tuple:
                - str: The final name assigned to the trace_styles_collection.
                - dict: Dictionary mapping trace_style names to their definitions.

        """
        if indices_of_data_series_to_extract_styles_from is None:  # should not initialize mutable objects in arguments line, so doing here.
            indices_of_data_series_to_extract_styles_from = []
        if new_trace_style_names_list is None:  # should not initialize mutable objects in arguments line, so doing here.
            new_trace_style_names_list = []
        auto_new_trace_styles_collection_name, new_trace_styles_collection_dictionary_without_name = self.extract_trace_styles_collection(new_trace_styles_collection_name=new_trace_styles_collection_name, indices_of_data_series_to_extract_styles_from=indices_of_data_series_to_extract_styles_from, new_trace_style_names_list = new_trace_style_names_list, extract_colors=extract_colors)
        if new_trace_styles_collection_name == '':
            new_trace_styles_collection_name = auto_new_trace_styles_collection_name
        if filename == '':
            filename = new_trace_styles_collection_name
        write_trace_styles_collection_to_file(trace_styles_collection=new_trace_styles_collection_dictionary_without_name, trace_styles_collection_name=new_trace_styles_collection_name, filename=filename)
        return new_trace_styles_collection_name, new_trace_styles_collection_dictionary_without_name
    def extract_trace_style_by_index(self, data_series_index, new_trace_style_name='', extract_colors=False):
        """
        Extract the trace_style from a specific data series in fig_dict by index.

        Args:
            data_series_index (int): Index of the data series to extract the trace_style from.
            new_trace_style_name (str): Optional name to assign to the extracted style. A default is generated if omitted.
            extract_colors (bool): If True, includes color attributes in the extracted styles. This is typically not recommended, because a trace_style with colors would prevent automatic coloring of series across a graph.

        Returns:
            dict: Dictionary containing the extracted trace_style, keyed by new_trace_style_name if provided.

        """
        extracted_trace_style = extract_trace_style_by_index(self.fig_dict, data_series_index, new_trace_style_name=new_trace_style_name, extract_colors=extract_colors)
        return extracted_trace_style
    def export_trace_style_by_index(self, data_series_index, new_trace_style_name='', filename='', extract_colors=False):
        """
        Extracts the trace style from a specific data series and exports it to a file for reuse.

        Parameters:
            data_series_index (int): Index of the data series to extract the trace style from.
            new_trace_style_name (str): Optional name to assign to the extracted style. Auto-generated if omitted.
            filename (str): File name to export the trace style to. Defaults to the trace style name.
            extract_colors (bool): If True, includes color attributes in the extracted styles. This is typically not recommended, because a trace_style with colors would prevent automatic coloring of series across a graph.

        Returns:
            dict: A dictionary containing the exported trace style, keyed by its name.

        """
        extracted_trace_style = extract_trace_style_by_index(self.fig_dict, data_series_index, new_trace_style_name=new_trace_style_name, extract_colors=extract_colors)
        new_trace_style_name = list(extracted_trace_style.keys())[0] #the extracted_trace_style will have a single key which is the style name.
        if filename == '': 
            filename = new_trace_style_name
        write_trace_style_to_file(trace_style_dict=extracted_trace_style[new_trace_style_name],trace_style_name=new_trace_style_name, filename=filename)
        return extracted_trace_style       
    ## End of section of JSONGRapher class functions related to styles ##

    #Make some pointers to external functions, for convenience, so people can use syntax like record.function_name() if desired.
    def validate_JSONGrapher_record(self):
        """
        Wrapper method that validates fig_dict using the external validate_JSONGrapher_record function.

        """
        validate_JSONGrapher_record(self)
    def update_and_validate_JSONGrapher_record(self, clean_for_plotly=True):
        """
        Trigger validation and optional cleaning of fig_dict using the external update_and_validate_JSONGrapher_record function.

        Args:
            clean_for_plotly (bool): If True (default), performs cleaning tailored for Plotly compatibility.

        """
        update_and_validate_JSONGrapher_record(self, clean_for_plotly=clean_for_plotly)


# helper function to validate x axis and y axis labels.
# label string will be the full label including units. Axis_name is typically "x" or "y"
def validate_JSONGrapher_axis_label(label_string, axis_name="", remove_plural_units=True):
    """
    Validates the axis label provided to JSONGrapher.

    Args:
        label_string (str): The axis label containing label text and units.
        axis_name (str): The name of the axis being validated (e.g., 'x' or 'y').
        remove_plural_units (bool): Whether to remove plural units. If True, modifies the label by converting units to singular. If False, issues a warning but leaves the units unchanged.

    Returns:
        tuple: (bool, list, str)
            - A boolean indicating whether the label passed validation.
            - A list of warning messages, if any.
            - The (potentially modified) label string.
    """
    warnings_list = []
    #First check if the label is empty.
    if label_string == '':
        warnings_list.append(f"Your {axis_name} axis label is an empty string. JSONGrapher records should not have empty strings for axis labels.")
    else:    
        parsing_result = separate_label_text_from_units(label_string)  # Parse the numeric value and units from the label string
        # Check if units are missing
        if parsing_result["units"] == "":
            warnings_list.append(f"Your {axis_name} axis label is missing units. JSONGrapher is expected to handle axis labels with units, with the units between parentheses '( )'.")    
        # Check if the units string has balanced parentheses
        open_parens = parsing_result["units"].count("(")
        close_parens = parsing_result["units"].count(")")
        if open_parens != close_parens:
            warnings_list.append(f"Your {axis_name} axis label has unbalanced parentheses in the units. The number of opening parentheses '(' must equal the number of closing parentheses ')'.")
    
    #now do the plural units check.
    units_changed_flag, units_singularized = units_plural_removal(parsing_result["units"])
    if units_changed_flag == True:
        warnings_list.append("The units of " + parsing_result["units"] + " appear to be plural. Units should be entered as singular, such as 'year' rather than 'years'.")
        if remove_plural_units==True:
            label_string = parsing_result["text"] + " (" + units_singularized + ")"
            warnings_list.append("Now removing the 's' to change the units into singular '" + units_singularized + "'.  To avoid this change, use the function you've called with the optional argument of remove_plural_units set to False.")
    else:
        pass

    # Return validation result
    if warnings_list:
        print(f"Warning: Your  {axis_name} axis label did not pass expected vaidation checks. You may use Record.set_x_axis_label() or Record.set_y_axis_label() to change the labels. The validity check fail messages are as follows: \n", warnings_list)
        return False, warnings_list, label_string
    else:
        return True, [], label_string    
    
def units_plural_removal(units_to_check):
    """
    Parses a units string and removes the trailing "s" if the singular form is recognized.

    Args:
        units_to_check (str): A string containing the units to validate and potentially singularize.

    Returns:
        tuple:
            - changed (bool): True if the input string was modified to remove a trailing "s"; otherwise, False.
            - singularized (str): The singular form of the input units, if modified; otherwise, the original string.
    """

    # Check if we have the module we need. If not, return with no change.
    try:
        import JSONGrapher.units_list as units_list
    except ImportError:
        try:
            from . import units_list  # Attempt local import
        except ImportError as exc:  # If still not present, give up and avoid crashing
            units_changed_flag = False
            print(f"Module import failed: {exc}")  # Log the error for debugging
            return units_changed_flag, units_to_check  # Return unchanged values

    #First try to check if units are blank or ends with "s" is in the units list. 
    if (units_to_check == "") or (units_to_check[-1] != "s"):
        units_changed_flag = False
        units_singularized = units_to_check #return if string is blank or does not end with s.
    elif (units_to_check != "") and (units_to_check[-1] == "s"): #continue if not blank and ends with s. 
        if (units_to_check in units_list.expanded_ids_set) or (units_to_check in units_list.expanded_names_set):#return unchanged if unit is recognized.
            units_changed_flag = False
            units_singularized = units_to_check #No change if was found.
        else:
            truncated_string = units_to_check[0:-1] #remove last letter.
            if (truncated_string in units_list.expanded_ids_set) or (truncated_string in units_list.expanded_names_set):
                units_changed_flag = True
                units_singularized = truncated_string #return without the s.   
            else: #No change if the truncated string isn't found.
                units_changed_flag = False
                units_singularized = units_to_check
    else:
        units_changed_flag = False
        units_singularized = units_to_check  #if it's outside of ourknown logic, we just return unchanged.
    return units_changed_flag, units_singularized


def separate_label_text_from_units(label_with_units):
    """
    Separates the main label text and the units text from a string. String must contain the main label text followed by units in parentheses, such as "Distance (km).

    Args:
        label_with_units (str): A label string expected to include units in parentheses, e.g., "Distance (km)".

    Returns:
        dict: A dictionary with two keys:
            - "text" (str): The portion of the label before the first opening parenthesis.
            - "units" (str): The content within the outermost pair of parentheses, or from the first '(' onward if parentheses are unbalanced internally.

    Raises:
        ValueError: If the number of opening and closing parentheses in the string do not match.
    """
    # Check for mismatched parentheses
    open_parentheses = label_with_units.count('(')
    close_parentheses = label_with_units.count(')')
    
    if open_parentheses != close_parentheses:
        raise ValueError(f"Mismatched parentheses in input string: '{label_with_units}'")

    # Default parsed output
    parsed_output = {"text": label_with_units, "units": ""}

    # Extract tentative start and end indices, from first open and first close parentheses.
    start = label_with_units.find('(')
    end = label_with_units.rfind(')')

    # Flag to track if the second check fails
    second_check_failed = False

    # Ensure removing both first '(' and last ')' doesn't cause misalignment
    if start != -1 and end != -1:
        temp_string = label_with_units[:start] + label_with_units[start + 1:end] + label_with_units[end + 1:]  # Removing first '(' and last ')'
        first_closing_paren_after_removal = temp_string.find(')')
        first_opening_paren_after_removal = temp_string.find('(')
        if first_opening_paren_after_removal != -1 and first_closing_paren_after_removal < first_opening_paren_after_removal:
            second_check_failed = True  # Set flag if second check fails

    if second_check_failed:
        #For the units, keep everything from the first '(' onward
        parsed_output["text"] = label_with_units[:start].strip()
        parsed_output["units"] = label_with_units[start:].strip()
    else:
        # Extract everything between first '(' and last ')'
        parsed_output["text"] = label_with_units[:start].strip()
        parsed_output["units"] = label_with_units[start + 1:end].strip()

    return parsed_output



def validate_plotly_data_list(data):
    """
    Validates the data series dictionaries in a list provided, also accepts a single data series dictionary instead of a list.

    If a single dictionary is passed, it is treated as a one-item list. The function checks each trace for the required
    structure and fields based on its inferred type (such as 'scatter', 'bar', 'pie', 'heatmap'). Warnings are printed for any issues found.

    Args:
        data (list or dict): A list of data series dictionaries (each for one Plotly traces), or a single data series dictionary.

    Returns:
        tuple:
            - bool: True if all traces are valid; False otherwise.
            - list: A list of warning messages describing why validation failed (if any).
    """
    #check if a dictionary was received. If so, will assume that
    #a single series has been sent, and will put it in a list by itself.
    if type(data) == type({}):
        data = [data]

    required_fields_by_type = {
        "scatter": ["x", "y"],
        "bar": ["x", "y"],
        "pie": ["labels", "values"],
        "heatmap": ["z"],
    }
    
    warnings_list = []

    for i, trace in enumerate(data):
        if not isinstance(trace, dict):
            warnings_list.append(f"Trace {i} is not a dictionary.")
            continue
        if "comments" in trace:
            warnings_list.append(f"Trace {i} has a comments field within the data. This is allowed by JSONGrapher, but is discouraged by plotly. By default, this will be removed when you export your record.")
        # Determine the type based on the fields provided
        trace_style = trace.get("type")
        if not trace_style:
            # Infer type based on fields and attributes
            if "x" in trace and "y" in trace:
                if "mode" in trace or "marker" in trace or "line" in trace:
                    trace_style = "scatter"
                elif "text" in trace or "marker.color" in trace:
                    trace_style = "bar"
                else:
                    trace_style = "scatter"  # Default assumption
            elif "labels" in trace and "values" in trace:
                trace_style = "pie"
            elif "z" in trace:
                trace_style = "heatmap"
            else:
                warnings_list.append(f"Trace {i} cannot be inferred as a valid type.")
                continue
        
        # Check for required fields
        required_fields = required_fields_by_type.get(trace_style, [])
        for field in required_fields:
            if field not in trace:
                warnings_list.append(f"Trace {i} (type inferred as {trace_style}) is missing required field: {field}.")

    if warnings_list:
        print("Warning: There are some entries in your data list that did not pass validation checks: \n", warnings_list)
        return False, warnings_list
    else:
        return True, []

def parse_units(value):
    """
    Parses strings containing numerical values aund units in parentheses, and extracts both the numerical value string and the units string.
    This is intended for scientific measurements, constants, or parameters, including the gravitational constant, rate constants, etc.
    It is not meant for separating axis labels from units; for that use `separate_label_text_from_units()` instead.

    Args:
        value (str): A string containing a numeric value and optional units enclosed in parentheses.
                     Example: "42 (kg)" or "100".

    Returns:
        dict: A dictionary with two keys:
              - "value" (float): The numeric value parsed from the input string.
              - "units" (str): The extracted units, or an empty string if no units are present.
    """

    # Find the position of the first '(' and the last ')'
    start = value.find('(')
    end = value.rfind(')')
    # Ensure both are found and properly ordered
    if start != -1 and end != -1 and end > start:
        number_part = value[:start].strip()  # Everything before '('
        units_part = value[start + 1:end].strip()  # Everything inside '()'
        parsed_output = {
            "value": float(number_part),  # Convert number part to float
            "units": units_part  # Extracted units
        }
    else:
        parsed_output = {
            "value": float(value),  # No parentheses, assume the entire string is numeric
            "units": ""  # Empty string represents absence of units
        }
    
    return parsed_output

#This function does updating of internal things before validating
#This is used before printing and returning the JSON record.
def update_and_validate_JSONGrapher_record(record, clean_for_plotly=True):
    """
    Updates internal properties of a JSONGrapher record and validates it.

    This function is typically called before exporting or printing the record to ensure it's clean
    and meets validation requirements. Optionally cleans the figure dictionary to make it Plotly-compatible.

    Args:
        record: A JSONGrapher Record object to update and validate.
        clean_for_plotly (bool): If True, cleans the `fig_dict` to match Plotly export requirements.

    Returns:
        The updated and validated record object.
    """
    record.validate_JSONGrapher_record()
    if clean_for_plotly == True:
        record.fig_dict = clean_json_fig_dict(record.fig_dict)
    return record

#TODO: add the ability for this function to check against the schema.
def validate_JSONGrapher_record(record):
    """
    Validates a JSONGrapher record to ensure all required fields are present and correctly structured.

    Args:
        record (dict): The JSONGrapher record to validate.

    Returns:
        tuple:
            - bool: True if the record is valid; False otherwise.
            - list: A list of warning messages describing any validation issues.
    """
    warnings_list = []

    # Check top-level fields
    if not isinstance(record, dict):
        return False, ["The record is not a dictionary."]
    
    # Validate "comments"
    if "comments" not in record:
        warnings_list.append("Missing top-level 'comments' field.")
    elif not isinstance(record["comments"], str):
        warnings_list.append("'comments' is a recommended field and should be a string with a description and/or metadata of the record, and citation references may also be included.")
    
    # Validate "datatype"
    if "datatype" not in record:
        warnings_list.append("Missing 'datatype' field.")
    elif not isinstance(record["datatype"], str):
        warnings_list.append("'datatype' should be a string.")
    
    # Validate "data"
    if "data" not in record:
        warnings_list.append("Missing top-level 'data' field.")
    elif not isinstance(record["data"], list):
        warnings_list.append("'data' should be a list.")
        validate_plotly_data_list(record["data"]) #No need to append warnings, they will print within that function.
    
    # Validate "layout"
    if "layout" not in record:
        warnings_list.append("Missing top-level 'layout' field.")
    elif not isinstance(record["layout"], dict):
        warnings_list.append("'layout' should be a dictionary.")
    else:
        # Validate "layout" subfields
        layout = record["layout"]
        
        # Validate "title"
        if "title" not in layout:
            warnings_list.append("Missing 'layout.title' field.")
        # Validate "title.text"
        elif "text" not in layout["title"]:
            warnings_list.append("Missing 'layout.title.text' field.")
        elif not isinstance(layout["title"]["text"], str):
            warnings_list.append("'layout.title.text' should be a string.")
        
        # Validate "xaxis"
        if "xaxis" not in layout:
            warnings_list.append("Missing 'layout.xaxis' field.")
        elif not isinstance(layout["xaxis"], dict):
            warnings_list.append("'layout.xaxis' should be a dictionary.")
        else:
            # Validate "xaxis.title"
            if "title" not in layout["xaxis"]:
                warnings_list.append("Missing 'layout.xaxis.title' field.")
            elif "text" not in layout["xaxis"]["title"]:
                warnings_list.append("Missing 'layout.xaxis.title.text' field.")
            elif not isinstance(layout["xaxis"]["title"]["text"], str):
                warnings_list.append("'layout.xaxis.title.text' should be a string.")
        
        # Validate "yaxis"
        if "yaxis" not in layout:
            warnings_list.append("Missing 'layout.yaxis' field.")
        elif not isinstance(layout["yaxis"], dict):
            warnings_list.append("'layout.yaxis' should be a dictionary.")
        else:
            # Validate "yaxis.title"
            if "title" not in layout["yaxis"]:
                warnings_list.append("Missing 'layout.yaxis.title' field.")
            elif "text" not in layout["yaxis"]["title"]:
                warnings_list.append("Missing 'layout.yaxis.title.text' field.")
            elif not isinstance(layout["yaxis"]["title"]["text"], str):
                warnings_list.append("'layout.yaxis.title.text' should be a string.")
    
    # Return validation result
    if warnings_list:
        print("Warning: There are missing fields in your JSONGrapher record: \n", warnings_list)
        return False, warnings_list
    else:
        return True, []

def rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2, num_interpolated_points=0, adjust_edges=True):
    """
    Applies a rolling polynomial regression to the data using a sliding window.

    Fits a polynomial of the specified degree to segments of the input data and optionally interpolates additional
    points between each segment. Edge behavior can be adjusted for smoother curve boundaries.

    Args:
        x_values (list): List of x-coordinate values.
        y_values (list): List of y-coordinate values.
        window_size (int): Number of data points per rolling fit window (default: 3).
        degree (int): Degree of the polynomial to fit within each window (default: 2).
        num_interpolated_points (int): Number of interpolated points between each pair of x-values (default: 0).
        adjust_edges (bool): If True, expands window size near edges for smoother transitions (default: True).

    Returns:
        tuple:
            - smoothed_x (list): List of x-values including interpolated points.
            - smoothed_y (list): List of corresponding y-values from the polynomial fits.
    """
    import numpy as np

    smoothed_y = []
    smoothed_x = []

    half_window = window_size // 2  # Number of points to take before & after

    for i in range(len(y_values) - 1):
        # Handle edge cases dynamically based on window size
        left_bound = max(0, i - half_window)
        right_bound = min(len(y_values), i + half_window + 1)

        if adjust_edges:
            if i == 0:  # First point
                right_bound = min(len(y_values), i + window_size)  # Expand to use more points near start
            elif i == len(y_values) - 2:  # Last point
                left_bound = max(0, i - (window_size - 1))  # Expand to include more points near end

        # Select the windowed data
        x_window = np.array(x_values[left_bound:right_bound])
        y_window = np.array(y_values[left_bound:right_bound])

        # Adjust degree based on window size
        adjusted_degree = degree if len(x_window) > 2 else 1  # Use linear fit if only two points are available

        # Fit polynomial & evaluate at current point
        poly_coeffs = np.polyfit(x_window, y_window, deg=adjusted_degree)

        # Generate interpolated points between x_values[i] and x_values[i+1]
        x_interp = np.linspace(x_values[i], x_values[i+1], num_interpolated_points + 2)  # Including endpoints
        y_interp = np.polyval(poly_coeffs, x_interp)

        smoothed_x.extend(x_interp)
        smoothed_y.extend(y_interp)

    return smoothed_x, smoothed_y



## Start of Section of Code for Styles and Converting between plotly and matplotlib Fig objectss ##
# #There are a few things to know about the styles logic of JSONGrapher:
# (1) There are actually two parts to the plot_style: a layout_style for the graph and a trace_styles_collection which will get applied to the individual dataseries.
#    So the plot_style is really supposed to be a dictionary with {"layout_style":"default", "trace_styles_collection":"default"} that way it is JSON compatible and avoids ambiguity. 
#    A person can pass in dictionaries for layout_style and for trace_styles_collection and thereby create custom styles.
#    There are helper functions to extract style dictionaries once a person has a JSONGrapher record which they're happy with.
# (2) We parse what the person provides as a style, so we accept things other than the ideal plot_style dictionary format.  
#    If someone provides a single string, we'll use it for both layout_style and trace_styles_collection.
#    If we get a list of two, we'll expect that to be in the order of layout_style then trace_styles_collection
#    If we get a string that we can't find in the existing styles list, then we'll use the default. 
# (1) by default, exporting a JSONGRapher record to file will *not* include plot_styles.  include_formatting will be an optional argument. 
# (2) There is an apply_plot_style function which will first put the style into self.fig_dict['plot_style'] so it stays there, before applying the style.
# (3) For the plotting functions, they will have plot_style = {"layout_style":"", "trace_styles_collection":""} or = '' as their default argument value, which will result in checking if plot_style exists in the self.fig_dict already. If so, it will be used. 
#     If somebody passes in a "None" type or the word none, then *no* style changes will be applied during plotting, relative to what the record already has.
#     One can pass a style in for the plotting functions. In those cases, we'll use the remove style option, then apply.

def parse_plot_style(plot_style):
    """
    Parses the given plot style and returns a structured dictionary for layout and trace styles.

    Accepts a variety of input formats and ensures a dictionary with "layout_style" and
    "trace_styles_collection" keys is returned. Defaults are applied if fields are missing.
    Also issues warnings for common key misspellings in dictionary input.

    Args:
        plot_style (None, str, list, or dict): The style input. Can be:
            - A dictionary with one or both expected keys
            - A list of two strings: [layout_style, trace_styles_collection]
            - A single string to use for both layout and trace styles
            - None

    Returns:
        dict: A dictionary with keys:
            - "layout_style" (str or None)
            - "trace_styles_collection" (str or None)
    """
    if plot_style is None:
        parsed_plot_style = {"layout_style": None, "trace_styles_collection": None}
    elif isinstance(plot_style, str):
        parsed_plot_style = {"layout_style": plot_style, "trace_styles_collection": plot_style}
    elif isinstance(plot_style, list) and len(plot_style) == 2:
        parsed_plot_style = {"layout_style": plot_style[0], "trace_styles_collection": plot_style[1]}
    elif isinstance(plot_style, dict):
        if "trace_styles_collection" not in plot_style:
            if "trace_style_collection" in plot_style:
                print("Warning: plot_style has 'trace_style_collection', this key should be 'trace_styles_collection'.  The key is being used, but the spelling error should be fixed.")
                plot_style["traces_styles_collection"] = plot_style["trace_style_collection"]
            elif "traces_style_collection" in plot_style:
                print("Warning: plot_style has 'traces_style_collection', this key should be 'trace_styles_collection'.  The key is being used, but the spelling error should be fixed.")
                plot_style["traces_styles_collection"] = plot_style["traces_style_collection"]
            else:
                plot_style.setdefault("trace_styles_collection", '')
        if "layout_style" not in plot_style: 
            plot_style.setdefault("layout_style", '')
        parsed_plot_style = {
            "layout_style": plot_style.get("layout_style", None),
            "trace_styles_collection": plot_style.get("trace_styles_collection", None),
        }
    else:
        raise ValueError("Invalid plot style: Must be None, a string, a list of two items, or a dictionary with valid fields.")
    return parsed_plot_style

#this function uses a stylename or list of stylename/dictionaries to apply *both* layout_style and trace_styles_collection
#plot_style is a dictionary of form {"layout_style":"default", "trace_styles_collection":"default"}
#However, the style_to_apply does not need to be passed in as a dictionary.
#For example: style_to_apply = ['default', 'default'] or style_to_apply = 'science'.
#IMPORTANT: This is the only function that will set a layout_style or trace_styles_collection that is an empty string into 'default'.
# all other style applying functions (including parse_plot_style) will pass on the empty string or will do nothing if receiving an empty string.
def apply_plot_style_to_plotly_dict(fig_dict, plot_style=None):
    """
    Applies both layout and trace styles to a Plotly figure dictionary based on the provided plot_style.

    Input plot_style can be a dictionary, list, or string. It is internally parsed and converted to a dictionary if needed via `parse_plot_style()`.
    This is the only style-applying function that substitutes empty strings with "default" styles in the dictionary itself.
    Having this as the only style-applying function that will convert empty strings to "default" within the dictionary is important for developers to maintain
    for the algorithmic flow for how styles are applied.    

    Args:
        fig_dict (dict): The Plotly figure dictionary to which styles will be applied.
        plot_style (str, list, or dict, optional): The style(s) to apply. Acceptable formats:
            - A single string (applied to both layout and trace styles).
            - A list of two strings: [layout_style, trace_styles_collection].
            - A dictionary with "layout_style" and/or "trace_styles_collection" keys.
            Defaults to {"layout_style": {}, "trace_styles_collection": {}}.

    Returns:
        dict: The modified Plotly figure dictionary with styles applied.
    """
    if plot_style is None:  # should not initialize mutable objects in arguments line, so doing here.
        plot_style = {"layout_style": {}, "trace_styles_collection": {}}  # Fresh dictionary per function call
    #We first parse style_to_apply to get a properly formatted plot_style dictionary of form: {"layout_style":"default", "trace_styles_collection":"default"}
    plot_style = parse_plot_style(plot_style)
    plot_style.setdefault("layout_style",'') #fill with blank string if not present.
    plot_style.setdefault("trace_styles_collection",'')  #fill with blank string if not present.
    #Code logic for layout style.
    if str(plot_style["layout_style"]).lower() != 'none': #take no action if received "None" or NoneType
        if plot_style["layout_style"] == '': #in this case, we're going to use the default.
            plot_style["layout_style"] = 'default'
            if "z" in fig_dict["data"][0]:
                print("Warning: No layout_style provided and 'z' field found in first data series. For 'bubble2d' plots, it is recommended to set layout_style to 'default'. For 'mesh3d' graphs and 'scatter3d' graphs, it is recommended to set layout_style to 'default3d'. Set layout_style to 'none' or another layout_style to avoid this warning.")
        fig_dict = remove_layout_style_from_plotly_dict(fig_dict=fig_dict)
        fig_dict = apply_layout_style_to_plotly_dict(fig_dict=fig_dict, layout_style_to_apply=plot_style["layout_style"])
    #Code logic for trace_styles_collection style.
    if str(plot_style["trace_styles_collection"]).lower() != 'none': #take no action if received "None" or NoneType
        if plot_style["trace_styles_collection"] == '': #in this case, we're going to use the default.
            plot_style["trace_styles_collection"] = 'default'            
        fig_dict = remove_trace_styles_collection_from_plotly_dict(fig_dict=fig_dict)
        fig_dict = apply_trace_styles_collection_to_plotly_dict(fig_dict=fig_dict,trace_styles_collection=plot_style["trace_styles_collection"])
    return fig_dict

def remove_plot_style_from_fig_dict(fig_dict):
    """
    Removes both layout and trace styles from a Plotly figure dictionary.

    This function strips custom layout and trace styling, resetting the figure
    to a default format suitable for clean export or re-styling.

    Args:
        fig_dict (dict): The Plotly figure dictionary to clean.

    Returns:
        dict: The updated figure dictionary with styles removed.
    """
    fig_dict = remove_layout_style_from_plotly_dict(fig_dict)
    fig_dict = remove_trace_styles_collection_from_plotly_dict(fig_dict)
    return fig_dict


def convert_JSONGrapher_dict_to_matplotlib_fig(fig_dict):
    """
    Converts a Plotly figure dictionary into a Matplotlib figure without relying on Plotly's `pio.from_json`.

    Currently supports basic conversion of bar and scatter-style traces. For `scatter_spline` and `spline`,
    a rolling polynomial fit is used as an approximation. Layout metadata such as title and axis labels
    are also extracted and applied to the Matplotlib figure.

    Args:
        fig_dict (dict): A dictionary representing a Plotly figure.

    Returns:
        matplotlib.figure.Figure: The corresponding Matplotlib figure object.
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()

    # Extract traces (data series)
    #This section is now deprecated. It has not been completely updated after the trace_style field was created.
    #There was old logic for plotly_trace_type which has been partially updated, but in fact the logic should be rewritten
    #to better accommodate the existence of both "trace_style" and "type". It may be that there should be
    #a helper function called 
    for trace in fig_dict.get("data", []):
        trace_style = trace.get("trace_style", '')
        plotly_trace_types = trace.get("type", '')
        if (plotly_trace_types == '') and (trace_style == ''):
            trace_style = 'scatter_spline'
        elif (plotly_trace_types == 'scatter') and (trace_style == ''):
            trace_style = 'scatter_spline'
        elif (trace_style == '') and (plotly_trace_types != ''):
            trace_style = plotly_trace_types
        # If type is missing, but mode indicates lines and shape is spline, assume it's a spline
        if not trace_style and trace.get("mode") == "lines" and trace.get("line", {}).get("shape") == "spline":
            trace_style = "spline"
        x_values = trace.get("x", [])
        y_values = trace.get("y", [])
        trace_name = trace.get("name", "Data")
        if trace_style == "bar":
            ax.bar(x_values, y_values, label=trace_name)
        elif trace_style == "scatter":
            mode = trace.get("mode", "")
            ax.scatter(x_values, y_values, label=trace_name, alpha=0.7)
        elif trace_style == "scatter_spline":
            mode = trace.get("mode", "")
            ax.scatter(x_values, y_values, label=trace_name, alpha=0.7)
            # Attempt to simulate spline behavior if requested
            if "lines" in mode or trace.get("line", {}).get("shape") == "spline":
                print("Warning: Rolling polynomial approximation used instead of spline.")
                x_smooth, y_smooth = rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2)
                # Add a label explicitly for the legend
                ax.plot(x_smooth, y_smooth, linestyle="-", label=f"{trace_name} Spline")
        elif trace_style == "spline":
            print("Warning: Using rolling polynomial approximation instead of true spline.")
            x_smooth, y_smooth = rolling_polynomial_fit(x_values, y_values, window_size=3, degree=2)
            ax.plot(x_smooth, y_smooth, linestyle="-", label=f"{trace_name} Spline")

    # Extract layout details
    layout = fig_dict.get("layout", {})
    title = layout.get("title", {})
    if isinstance(title, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        ax.set_title(title.get("text", "Converted Plotly Figure"))
    else:
        ax.set_title(title if isinstance(title, str) else "Converted Plotly Figure")

    xaxis = layout.get("xaxis", {})
    xlabel = "X-Axis"  # Default label
    if isinstance(xaxis, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        title_obj = xaxis.get("title", {})
        xlabel = title_obj.get("text", "X-Axis") if isinstance(title_obj, dict) else title_obj
    elif isinstance(xaxis, str):
        xlabel = xaxis  # If it's a string, use it directly
    ax.set_xlabel(xlabel)
    yaxis = layout.get("yaxis", {})
    ylabel = "Y-Axis"  # Default label
    if isinstance(yaxis, dict): #This if statements block is rather not human readable. Perhaps should be changed later.
        title_obj = yaxis.get("title", {})
        ylabel = title_obj.get("text", "Y-Axis") if isinstance(title_obj, dict) else title_obj
    elif isinstance(yaxis, str):
        ylabel = yaxis  # If it's a string, use it directly
    ax.set_ylabel(ylabel)
    ax.legend()
    return fig
    
def convert_plotly_dict_to_matplotlib(fig_dict):
    """
    Converts a Plotly figure dictionary into a Matplotlib figure.

    Supports basic translation of Bar Charts, Scatter Plots, and Spline curves
    (the latter simulated using a rolling polynomial fit).

    Args:
        fig_dict (dict): A dictionary representing a Plotly figure.

    Returns:
        matplotlib.figure.Figure: The created Matplotlib figure object.
    """
    import plotly.io as pio
    import matplotlib.pyplot as plt
    # Convert JSON dictionary into a Plotly figure
    plotly_fig = pio.from_json(json.dumps(fig_dict))

    # Create a Matplotlib figure
    fig, ax = plt.subplots()

    for trace in plotly_fig.data:
        if trace.type == "bar":
            ax.bar(trace.x, trace.y, label=trace.name if trace.name else "Bar Data")

        elif trace.type == "scatter":
            mode = trace.mode if isinstance(trace.mode, str) else ""
            line_shape = trace.line["shape"] if hasattr(trace, "line") and "shape" in trace.line else None

            # Plot raw scatter points
            ax.scatter(trace.x, trace.y, label=trace.name if trace.name else "Scatter Data", alpha=0.7)

            # If spline is requested, apply rolling polynomial smoothing
            if line_shape == "spline" or "lines" in mode:
                print("Warning: During the matploglib conversion, a rolling polynomial will be used instead of a spline, whereas JSONGrapher uses a true spline.")
                x_smooth, y_smooth = rolling_polynomial_fit(trace.x, trace.y, window_size=3, degree=2)
                ax.plot(x_smooth, y_smooth, linestyle="-", label=trace.name + " Spline" if trace.name else "Spline Curve")

    ax.legend()
    ax.set_title(plotly_fig.layout.title.text if plotly_fig.layout.title else "Converted Plotly Figure")
    ax.set_xlabel(plotly_fig.layout.xaxis.title.text if plotly_fig.layout.xaxis.title else "X-Axis")
    ax.set_ylabel(plotly_fig.layout.yaxis.title.text if plotly_fig.layout.yaxis.title else "Y-Axis")

    return fig

def apply_trace_styles_collection_to_plotly_dict(fig_dict, trace_styles_collection="", trace_style_to_apply=""):
    """
    Applies a trace style preset to each trace in a Plotly figure dictionary.

    Iterates over all traces in `fig_dict["data"]` and updates their appearance using the
    provided `trace_styles_collection`. Also sets/updates the applied trace_styles_collection name in `fig_dict["plot_style"]`.

    Args:
        fig_dict (dict): A dictionary containing a Plotly-style `data` list of traces.
        trace_styles_collection (str or dict): A named style collection or a full style definition dictionary.
        trace_style_to_apply (str): Optional specific trace style to apply to each series (default is "").

    Returns:
        dict: The updated Plotly figure dictionary with applied trace styles.
    """
    if type(trace_styles_collection) == type("string"):
        trace_styles_collection_name = trace_styles_collection
    else:
        trace_styles_collection_name = trace_styles_collection["name"]

    if "data" in fig_dict and isinstance(fig_dict["data"], list):
        fig_dict["data"] = [apply_trace_style_to_single_data_series(data_series=trace,trace_styles_collection=trace_styles_collection, trace_style_to_apply=trace_style_to_apply) for trace in fig_dict["data"]]
    
    if "plot_style" not in fig_dict:
        fig_dict["plot_style"] = {}
    fig_dict["plot_style"]["trace_styles_collection"] = trace_styles_collection_name
    return fig_dict


# The logic in JSONGrapher is to apply the style information but to treat "type" differently 
# Accordingly, we use 'trace_styles_collection' as a field in JSONGrapher for each data_series.
# compared to how plotly treats 'type' for a data series. So later in the process, when actually plotting with plotly, the 'type' field will get overwritten.
def apply_trace_style_to_single_data_series(data_series, trace_styles_collection="", trace_style_to_apply=""):
    """
    Applies a predefined or custom trace style to a single data series while preserving other fields.

    This trace_style_to_apply can be passed in as a dictionary or as a string that is a trace_style name to find in a trace_styles_collection 
    The function applies type-specific formatting (e.g., spline, scatterd3d, bubble2d), and conditionally injects colorscale mappings
    when specified via a trace-style suffix after a double underscore "__" delimeter  (e.g., "scatter__viridis").
    This function also calls helper functions to populate the sizes for bubble2d and bubble3d plots.

    Args:
        data_series (dict): A dictionary representing a single data series / trace.
        trace_styles_collection (str or dict): Name of the trace_styles_collection to use or a full trace_style_styles_collection dictionary. If
            empty, the 'default' trace_styles_collection will be used.
        trace_style_to_apply (str or dict): A specific trace_style name to pull from the trace_styles_collection or full style definition to apply. If
            empty, the function will check `data_series["trace_style"]` before using the 'default' trace_style.

    Returns:
        dict: The updated data series dictionary with applied style formatting.

    Notes:
        - Trace styles support 2D and 3D formats including "scatter", "scatter3d", "mesh3d", "heatmap", and "bubble".
        - A style suffix like "__viridis" triggers automatic colorscale assignment for markers, lines, or intensity maps.
        - If no valid style is found, the function falls back to the first available style in the collection.
        - None values in color-mapped data are converted to 0 and produce a warning.
    """
    if not isinstance(data_series, dict):
        return data_series  # Return unchanged if the data series is invalid.
    if isinstance(trace_style_to_apply, dict):#in this case, we'll set the data_series trace_style to match.
        data_series["trace_style"] = trace_style_to_apply
    if str(trace_style_to_apply) != str(''): #if we received a non-empty string (or dictionary), we'll put it into the data_series object.
        data_series["trace_style"] = trace_style_to_apply
    elif str(trace_style_to_apply) == str(''): #If we received an empty string for the trace_style_to apply (default JSONGrapher flow), we'll check in the data_series object.   
        #first see if there is a trace_style in the data_series.
        trace_style_to_apply = data_series.get("trace_style", "")
        #If it's "none", then we'll return the data series unchanged.
        #We consider it that for every trace_styles_collection, that "none" means to make no change.
        if str(trace_style_to_apply).lower() == "none":
            return data_series
        #if we find a dictionary, we will set the trace_style_to_apply to that, to ensure we skip other string checks to use the dictionary.
        if isinstance(trace_style_to_apply,dict):
            trace_style_to_apply = trace_style_to_apply
    #if the trace_style_to_apply is a string and we have not received a trace_styles collection, then we have nothing
    #to use, so will return the data_series unchanged.
    if type(trace_style_to_apply) == type("string"):
        if (trace_styles_collection == '') or (str(trace_styles_collection).lower() == 'none'):
            return data_series    
    #if the trace_style_to_apply is "none", we will return the series unchanged.
    if str(trace_style_to_apply).lower() == str("none"):
        return data_series
    #Add a couple of hardcoded cases.
    if type(trace_style_to_apply) == type("string"):
        if (trace_style_to_apply.lower() == "nature") or (trace_style_to_apply.lower() == "science"):
            trace_style_to_apply = "default"
    #Because the 3D traces will not plot correctly unless recognized,
    #we have a hardcoded case for the situation that 3D dataset is received without plot style.
    if trace_styles_collection == "default":
        if trace_style_to_apply == "":
            if data_series.get("z", '') != '':
                trace_style_to_apply = "scatter3d"
                uid = data_series.get('uid', '')
                name = data_series.get("name", '')
                print("Warning: A dataseries was found with no trace_style but with a 'z' field. " , "uid: " , uid ,  " . " + "name:",  name ,  " . The trace style for this dataseries is being set to scatter3d.")


    #at this stage, should remove any existing formatting before applying new formatting.
    data_series = remove_trace_style_from_single_data_series(data_series)

    # -------------------------------
    # Predefined trace_styles_collection
    # -------------------------------
    # Each trace_styles_collection is defined as a dictionary containing multiple trace_styles.
    # Users can select a style preset trace_styles_collection (e.g., "default", "minimalist", "bold"),
    # and this function will apply appropriate settings for the given trace_style.
    #
    # Examples of Supported trace_styles:
    # - "scatter_spline" (default when type is not specified)
    # - "scatter"
    # - "spline"
    # - "bar"
    # - "heatmap"
    #
    # Note: Colors are intentionally omitted to allow users to define their own.
    # However, predefined colorscales are applied for heatmaps.


    styles_available = JSONGrapher.styles.trace_styles_collection_library.styles_library

    # Get the appropriate style dictionary
    if isinstance(trace_styles_collection, dict):
        styles_collection_dict = trace_styles_collection  # Use custom style directly
    else:
        styles_collection_dict = styles_available.get(trace_styles_collection, {})
        if not styles_collection_dict:  # Check if it's an empty dictionary
            print(f"Warning: trace_styles_collection named '{trace_styles_collection}' not found. Using 'default' trace_styles_collection instead.")
            styles_collection_dict = styles_available.get("default", {})
    # Determine the trace_style, defaulting to the first item in a given style if none is provided.

    # Retrieve the specific style for the plot type
    if trace_style_to_apply == "":# if a trace_style_to_apply has not been supplied, we will get it from the dataseries.
        trace_style = data_series.get("trace_style", "")
    else:
        trace_style = trace_style_to_apply
    if trace_style == "": #if the trace style is an empty string....
        trace_style = list(styles_collection_dict.keys())[0] #take the first trace_style name in the style_dict.  In python 3.7 and later dictionary keys preserve ordering.

    #If a person adds "__colorscale" to the end of a trace_style, like "scatter_spline__rainbow" we will extract the colorscale and apply it to the plot.
    #This should be done before extracting the trace_style from the styles_available, because we need to split the string to break out the trace_style
    #Also should be initialized before determining the second half of colorscale_structure checks (which occurs after the trace_style application), since it affects that logic.
    colorscale = "" #initializing variable.
    if isinstance(trace_style, str): #check if it is a string type.
        if "__" in trace_style:
            trace_style, colorscale = trace_style.split("__")
        if ("bubble" in trace_style) and ("bubble3d" not in trace_style) and ("bubble2d" not in trace_style):
            trace_style = trace_style.replace("bubble", "bubble2d")

    colorscale_structure = "" #initialize this variable for use later. It tells us which fields to put the colorscale related values in. This should be done before regular trace_style fields are applied.
    #3D and bubble plots will have a colorscale by default.
    if isinstance(trace_style,str):
        if "bubble" in trace_style.lower(): #for bubble trace styles (both 2D and 3D), we need to prepare the bubble sizes. We also need to do this before the styles_dict collection is accessed, since then the trace_style becomes a dictionary.
            data_series = prepare_bubble_sizes(data_series)
            colorscale_structure = "bubble"
        elif "mesh3d" in trace_style.lower(): 
            colorscale_structure = "mesh3d"
        elif "scatter3d" in trace_style.lower(): 
            colorscale_structure = "scatter3d"

    if trace_style in styles_collection_dict:
        trace_style = styles_collection_dict.get(trace_style)
    elif trace_style not in styles_collection_dict:  # Check if it's an empty dictionary
        print(f"Warning: trace_style named '{trace_style}' not found in trace_styles_collection '{trace_styles_collection}'. Using the first trace_style in in trace_styles_collection '{trace_styles_collection}'.")
        trace_style = list(styles_collection_dict.keys())[0] #take the first trace_style name in the style_dict.  In python 3.7 and later dictionary keys preserve ordering.
        trace_style = styles_collection_dict.get(trace_style)

    # Apply type and other predefined settings
    data_series["type"] = trace_style.get("type")  
    # Apply other attributes while preserving existing values
    for key, value in trace_style.items():
        if key not in ["type"]:
            if isinstance(value, dict):  # Ensure value is a dictionary
                data_series.setdefault(key, {}).update(value)
            else:
                data_series[key] = value  # Direct assignment for non-dictionary values

    #Before applying colorscales, we check if we have recieved a colorscale from the user. If so, we'll need to parse the trace_type to assign the colorscale structure.
    if ((colorscale_structure == "") and (colorscale != "")):
        #If it is a scatter plot with markers, then the colorscale_structure will be marker. Need to check for this before the lines alone case.
        if ("markers" in data_series["mode"]) or ("markers+lines" in data_series["mode"]) or ("lines+markers" in data_series["mode"]):
            colorscale_structure = "marker"
        elif ("lines" in data_series["mode"]):
            colorscale_structure = "line"
        elif ("bar" in data_series["type"]):
            colorscale_structure = "marker"

    #Block of code to clean color values for 3D plots and 2D plots. It can't be just from the style dictionary because we need to point to data.
    def clean_color_values(list_of_values, variable_string_for_warning):
        if None in list_of_values:
            print("Warning: A colorscale based on " + variable_string_for_warning + " was requested. None values were found. They are being replaced with 0 values. It is recommended to provide data without None values.")
            color_values = [0 if value is None else value for value in list_of_values]
        else:
            color_values = list_of_values
        return color_values

    if colorscale_structure == "bubble":
        #data_series["marker"]["colorscale"] = "viridis_r" #https://plotly.com/python/builtin-colorscales/
        if colorscale != "": #this means there is a user specified colorscale.
            data_series["marker"]["colorscale"] = colorscale
        data_series["marker"]["showscale"] = True
        if "z" in data_series:
            color_values = clean_color_values(list_of_values= data_series["z"], variable_string_for_warning="z")
            data_series["marker"]["color"] = color_values
        elif "z_points" in data_series:
            color_values = clean_color_values(list_of_values= data_series["z_points"], variable_string_for_warning="z_points")
            data_series["marker"]["color"] = color_values
    elif colorscale_structure == "scatter3d":
        #data_series["marker"]["colorscale"] = "viridis_r" #https://plotly.com/python/builtin-colorscales/
        if colorscale != "": #this means there is a user specified colorscale.
            data_series["marker"]["colorscale"] = colorscale
        data_series["marker"]["showscale"] = True
        if "z" in data_series:
            color_values = clean_color_values(list_of_values= data_series["z"], variable_string_for_warning="z")
            data_series["marker"]["color"] = color_values
        elif "z_points" in data_series:
            color_values = clean_color_values(list_of_values= data_series["z_points"], variable_string_for_warning="z_points")
            data_series["marker"]["color"] = color_values
    elif colorscale_structure == "mesh3d":
        #data_series["colorscale"] = "viridis_r" #https://plotly.com/python/builtin-colorscales/
        if colorscale != "": #this means there is a user specified colorscale.
            data_series["colorscale"] = colorscale
        data_series["showscale"] = True
        if "z" in data_series:
            color_values = clean_color_values(list_of_values= data_series["z"], variable_string_for_warning="z")
            data_series["intensity"] = color_values
        elif "z_points" in data_series:
            color_values = clean_color_values(list_of_values= data_series["z_points"], variable_string_for_warning="z_points")
            data_series["intensity"] = color_values
    elif colorscale_structure == "marker":
        data_series["marker"]["colorscale"] = colorscale
        data_series["marker"]["showscale"] = True
        color_values = clean_color_values(list_of_values=data_series["y"], variable_string_for_warning="y")
        data_series["marker"]["color"] = color_values
    elif colorscale_structure == "line":
        data_series["line"]["colorscale"] = colorscale
        data_series["line"]["showscale"] = True
        color_values = clean_color_values(list_of_values=data_series["y"], variable_string_for_warning="y")
        data_series["line"]["color"] = color_values
        
            
    return data_series

def prepare_bubble_sizes(data_series):
    """
    Prepares a bubble sizes list for a bubble plot based on the fields provided in the data series,
    then inserts the bubble sizes list into the right field for a bubble plot.

    This function extracts bubble size values from a data_series field based on 'bubble_sizes' or the `z_points` or `z` field, 
    then scales the bubble sizes to a maximum value, `max_bubble_size`, with a default used if not provided by the data_series. 
    The function a also sets the `text` field of each marker point (each bubble) for hover display.

    Args:
        data_series (dict): A dictionary representing a single data series, with optional
                            fields such as 'bubble_sizes', and 'max_bubble_size'.

    Returns:
        dict: The updated data series with bubble sizes (marker sizes) and hover text inserted.

    Raises:
        KeyError: If no valid source of size data is found and/or bubble size scaling cannot proceed.
    """
    #To make a bubble plot with plotly, we are actually using a 2D plot
    #and are using the z values in a data_series to create the sizes of each point.
    #We also will scale them to some maximum bubble size that is specifed.
    if "marker" not in data_series:
        data_series["marker"] = {}   
    if "bubble_sizes" in data_series:
        if isinstance(data_series["bubble_sizes"], str): #if bubble sizes is a string, it must be a variable name to use for the bubble sizes.
            bubble_sizes_variable_name = data_series["bubble_sizes"]
            data_series["marker"]["size"] = data_series[bubble_sizes_variable_name]
        else:
            data_series["marker"]["size"] = data_series["bubble_sizes"]
    elif "z_points" in data_series:
        data_series["marker"]["size"] = data_series["z_points"]
    elif "z" in data_series:
        data_series["marker"]["size"] = data_series["z"]
    elif "y" in data_series:
        data_series["marker"]["size"] = data_series["y"]

    #now need to normalize to the max value in the list.
    def normalize_to_max(starting_list):
        import numpy as np
        arr = np.array(starting_list)  # Convert list to NumPy array for efficient operations
        max_value = np.max(arr)  # Find the maximum value in the list
        if max_value == 0:
            normalized_values = np.zeros_like(arr)  # If max_value is zero, return zeros
        else:
            normalized_values = arr / max_value  # Otherwise, divide each element by max_value           
        return normalized_values  # Return the normalized values
    try:
        normalized_sizes = normalize_to_max(data_series["marker"]["size"])
    except KeyError as exc:
        raise KeyError("Error: During bubble plot bubble size normalization, there was an error. This usually means the z variable has not been populated. For example, by equation evaluation set to false or simulation evaluation set to false.")

        
    #Now biggest bubble is 1 (or 0) so multiply to enlarge to scale.
    if "max_bubble_size" in data_series:
        max_bubble_size = data_series["max_bubble_size"]
    else:
        max_bubble_size = 100       
    scaled_sizes = normalized_sizes*max_bubble_size
    data_series["marker"]["size"] = scaled_sizes.tolist() #from numpy array back to list.
    
    #Now let's also set the text that appears during hovering to include the original data.
    if "z_points" in data_series:
        data_series["text"] = data_series["z_points"]
    elif "z" in data_series:
        data_series["text"] = data_series["z"]

    return data_series


#TODO: This logic should be changed in the future. There should be a separated function to remove formatting
# versus just removing the current setting of "trace_styles_collection"
# So the main class function will also be broken into two and/or need to take an optional argument in
def remove_trace_styles_collection_from_plotly_dict(fig_dict):
    """
    Removes trace styles from all data series in a Plotly figure dictionary.

    This function iterates through each trace in `fig_dict["data"]` and strips out applied
    style formatting—unless the trace's `trace_style` is explicitly set to "none". It also removes
    the `trace_styles_collection` reference from the figure's `plot_style` metadata.

    Args:
        fig_dict (dict): A Plotly-formatted figure dictionary.

    Returns:
        dict: The updated figure dictionary with trace styles removed.
    """
    #will remove formatting from the individual data_series, but will not remove formatting from any that have trace_style of "none".
    if isinstance(fig_dict, dict) and "data" in fig_dict and isinstance(fig_dict["data"], list):
        updated_data = []  # Initialize an empty list to store processed traces
        for trace in fig_dict["data"]:
            # Check if the trace has a "trace_style" field and if its value is "none" (case-insensitive)
            if trace.get("trace_style", "").lower() == "none":
                updated_data.append(trace)  # Skip modification and keep the trace unchanged
            else:
                # Apply the function to modify the trace before adding it to the list
                updated_data.append(remove_trace_style_from_single_data_series(trace))
        # Update the "data" field with the processed traces
        fig_dict["data"] = updated_data


    #If being told to remove the style, should also pop it from fig_dict.
    if "plot_style" in fig_dict:
        if "trace_styles_collection" in fig_dict["plot_style"]:
            fig_dict["plot_style"].pop("trace_styles_collection")
    return fig_dict

def remove_trace_style_from_single_data_series(data_series):
    """
    Removes style-related formatting fields from a single Plotly data series.

    This function strips only visual styling attributes (e.g., marker, line, fill) while preserving all
    other metadata and custom fields such as equations or simulation details. The result is returned as a
    `JSONGrapherDataSeries` object with key values preserved.

    Args:
        data_series (dict): A dictionary representing a single Plotly-style trace.

    Returns:
        JSONGrapherDataSeries: The cleaned data series with formatting fields removed.
    """

    if not isinstance(data_series, dict):
        return data_series  # Return unchanged if input is invalid.

    # **Define formatting fields to remove**
    formatting_fields = {
        "mode", "line", "marker", "colorscale", "opacity", "fill", "fillcolor", "color", "intensity", "showscale",
        "legendgroup", "showlegend", "textposition", "textfont", "visible", "connectgaps", "cliponaxis", "showgrid"
    }

    # **Create a new data series excluding only formatting fields**
    cleaned_data_series = {key: value for key, value in data_series.items() if key not in formatting_fields}
    #make the new data series into a JSONGrapherDataSeries object.
    new_data_series_object = JSONGrapherDataSeries()
    new_data_series_object.update_while_preserving_old_terms(cleaned_data_series)
    return new_data_series_object

def extract_trace_style_by_index(fig_dict, data_series_index, new_trace_style_name='', extract_colors=False):
    """
    Pulls a data_series dictionary from a fig_dict by the index,
    then creates a and returns a trace_style dictionary by extracting formatting attributes from that single data_series dictionary.

    This is a wrapper for `extract_trace_style_from_data_series_dict()` and allows optional renaming
    of the extracted style and optional extraction of color attributes. Extraction of color for the
    trace_style is not recommended for normal usage, since a color in a trace_style
    that overrides auto-coloring schemes when multiple series are present.

    Args:
        fig_dict (dict): A fig_dict with a `data` field containing a list of data_series dictionaries.
        data_series_index (int): Index of the target data series within the `data` list.
        new_trace_style_name (str): Optional new name to assign to the extracted trace_style.
        extract_colors (bool): Whether to include color-related attributes in the extracted trace_style.

    Returns:
        dict: A dictionary containing the extracted trace style.
    """
    data_series_dict = fig_dict["data"][data_series_index]
    extracted_trace_style = extract_trace_style_from_data_series_dict(data_series_dict=data_series_dict, new_trace_style_name=new_trace_style_name, extract_colors=extract_colors)
    return extracted_trace_style

def extract_trace_style_from_data_series_dict(data_series_dict, new_trace_style_name='', additional_attributes_to_extract=None, extract_colors=False):
    """
    Creates a and returns a trace_style dictionary by extracting formatting attributes from a single data_series dictionary.

    This function returns a trace_style dictionary containing only style-format related fields such as line, marker,
    and text formatting. Color values (e.g., fill, marker color) can optionally  be included in the extracted trace_style. 
    Extraction of color for the trace_style is not recommended for normal usage,
    since a color in a trace_style that overrides auto-coloring schemes when multiple series are present.

    Examples of formatting attributes extracted:
    - "type"
    - "mode"
    - "line"
    - "marker"
    - "colorscale"
    - "opacity"
    - "fill"
    - "legendgroup"
    - "showlegend"
    - "textposition"
    - "textfont"

    Args:
        data_series_dict (dict): A data_series dictionary for a single trace.
        new_trace_style_name (str): Optional name to assign the extracted style. If empty, the value in
                                    the `trace_style` field of the existing data_series dict will be used (if it is a string),
                                    and if no string is present there then "custom" will be used.
        additional_attributes_to_extract (list, optional): Additional formatting attributes to extract.
        extract_colors (bool): If set to True, will also extract color-related values like 'marker.color' and 'fillcolor'. Not recommended for typical trace_style usage.
    
    Returns:
        dict: A trace style dictionary with the format {style_name: formatting_attributes}.

    """  
    if additional_attributes_to_extract is None: #in python, it's not good to make an empty list a default argument.
        additional_attributes_to_extract = []

    if new_trace_style_name=='':
        #Check if there is a current trace style that is a string, and use that for the name if present.
        current_trace_style = data_series_dict.get("trace_style", "")
        if isinstance(current_trace_style, str):
           new_trace_style_name = current_trace_style
    #if there is still no new_trace_style_name, we will name it 'custom'
    if new_trace_style_name=='':
        new_trace_style_name = "custom"

    if not isinstance(data_series_dict, dict):
        return {}  # Return an empty dictionary if input is invalid.

    # Define known formatting attributes. This is a set (not a dictionary, not a list)
    formatting_fields = {
        "type", "mode", "line", "marker", "colorscale", "opacity", "fill", "fillcolor", "color", "intensity", "showscale",
        "legendgroup", "showlegend", "textposition", "textfont", "visible", "connectgaps", "cliponaxis", "showgrid"
    }

    formatting_fields.update(additional_attributes_to_extract)
    # Extract only formatting-related attributes
    trace_style_dict = {key: value for key, value in data_series_dict.items() if key in formatting_fields}

    #Pop out colors if we are not extracting them.
    if extract_colors == False:
        if "marker" in trace_style_dict:
            if "color" in trace_style_dict["marker"]:
                trace_style_dict["marker"].pop("color")
        if "line" in trace_style_dict:
            if "color" in trace_style_dict["line"]:
                trace_style_dict["line"].pop("color")
        if "colorscale" in trace_style_dict:  # Handles top-level colorscale for heatmaps, choropleths
            trace_style_dict.pop("colorscale")
        if "fillcolor" in trace_style_dict:  # Handles fill colors
            trace_style_dict.pop("fillcolor")
        if "textfont" in trace_style_dict:
            if "color" in trace_style_dict["textfont"]:  # Handles text color
                trace_style_dict["textfont"].pop("color")
        if "legendgrouptitle" in trace_style_dict and isinstance(trace_style_dict["legendgrouptitle"], dict):
            if "font" in trace_style_dict["legendgrouptitle"] and isinstance(trace_style_dict["legendgrouptitle"]["font"], dict):
                if "color" in trace_style_dict["legendgrouptitle"]["font"]:
                    trace_style_dict["legendgrouptitle"]["font"].pop("color")
    extracted_trace_style = {new_trace_style_name : trace_style_dict} #this is a trace_style dict.
    return extracted_trace_style #this is a trace_style dict.

#export a single trace_style dictionary to .json.
def write_trace_style_to_file(trace_style_dict, trace_style_name, filename):
    """
    Exports a single trace style dictionary to a JSON file.

    Wraps the trace style under a standard JSON structure with a named identifier and writes it to disk.
    Ensures the filename ends with ".json" for compatibility.

    Args:
        trace_style_dict (dict): A dictionary defining a single trace style.
        trace_style_name (str): The name to assign to the trace style within the exported file.
        filename (str): The target filename for the output JSON (with or without ".json").

    Returns:
        None
    """
    # Ensure the filename ends with .json
    if not filename.lower().endswith(".json"):
        filename += ".json"

    json_structure = {
        "trace_style": {
            "name": trace_style_name,
            trace_style_name: {
                trace_style_dict
            }
        }
    }

    with open(filename, "w", encoding="utf-8") as file:  # Specify UTF-8 encoding for compatibility
        json.dump(json_structure, file, indent=4)


#export an entire trace_styles_collection to .json. The trace_styles_collection is dict.
def write_trace_styles_collection_to_file(trace_styles_collection, trace_styles_collection_name, filename):   
    """
    Exports a trace_styles_collection dictionary to a JSON file.

    Accepts a trace_styles_collection dictionary and writes it to disk. 
    The trace_styeles_collection could be provided in a containing dictionary.
    So the function, first checks if the dictionary recieved has a key named "traces_tyles_collection".
    If that key is present, the function, pulls the traces_style_collection out of that field and uses it.

    Args:
        trace_styles_collection (dict): trace_styles_collection dictionary to export. Or a container with a trace_styles_collection inside.
        trace_styles_collection_name (str): The name for the trace_styles_collection to export, so it can later be used in the JSONGrapher styles_library
        filename (str): filename to write to. The function Automatically appends ".json" if a filename without file extension is provided.

    Returns:
        None
    """
    if "trace_styles_collection" in trace_styles_collection: #We may receive a traces_style collection in a container. If so, we pull the traces_style_collection out.
        trace_styles_collection = trace_styles_collection[trace_styles_collection["name"]] 
    # Ensure the filename ends with .json
    if not filename.lower().endswith(".json"):
        filename += ".json"

    json_structure = {
        "trace_styles_collection": {
            "name": trace_styles_collection_name,
            trace_styles_collection_name: trace_styles_collection
        }
    }

    with open(filename, "w", encoding="utf-8") as file:  # Specify UTF-8 encoding for compatibility
        json.dump(json_structure, file, indent=4)



#import an entire trace_styles_collection from .json. THe trace_styles_collection is dict.
def import_trace_styles_collection(filename):
    """
    Imports a trace_styles_collection dictionary from a JSON file.

    Reads a JSON-formatted file and extracts the trace_styles_collection
    identified by its embedded name. The function validates structure and
    ensures the expected format before returning the trace_styles_dictionary.
    If there is no name in the dictionary, the dictionary is assumed to
    be a trace_styles_collection dictionary, and the filename is used as the name.

    Args:
        filename (str): The name of the JSON file to import from. If the extension is
                        missing, ".json" will be appended automatically.

    Returns:
        dict: A dictionary containing the imported trace_styles_collection, or a trace_styles_collection dict directly.

    Raises:
        ValueError: If the JSON structure is malformed or the collection name is not found.
    """
    import os
    # Ensure the filename ends with .json. Add that extension if it's not present.
    if not filename.lower().endswith(".json"):
        filename += ".json"
    with open(filename, "r", encoding="utf-8") as file:  # Specify UTF-8 encoding for compatibility
        data = json.load(file)

    # Validate JSON structure
    dict_from_file = data.get("trace_styles_collection")
    if not isinstance(dict_from_file, dict):
        raise ValueError("Error: Missing or malformed 'trace_styles_collection'.")

    collection_name = dict_from_file.get("name") #check if the dictionary has a name field.
    if not isinstance(collection_name, str) or collection_name not in dict_from_file:
        # Use filename without extension if there is no name field in the dictionary.
        collection_name = os.path.splitext(os.path.basename(filename))[0]
        trace_styles_collection = dict_from_file #Take the dictionary received directly, assume there is no containing dict.
    else: #This is actually the normal case, that the trace_styles_collection will be in a containing dictionary.
        trace_styles_collection  = dict_from_file[collection_name]
    # Return only the dictionary corresponding to the collection name
    return trace_styles_collection

#import a single trace_styles dict from  a .json file.
def import_trace_style(filename):
    """
    Imports a single trace style from a JSON file.

    Reads a JSON-formatted file that contains a `trace_style` block and returns the
    associated trace style dictionary identified by its embedded name. Validates structure
    before returning the style.

    Args:
        filename (str): The name of the JSON file to import. If the extension is missing,
                        ".json" will be appended automatically.

    Returns:
        dict: A dictionary representing the imported trace_style.

    Raises:
        ValueError: If the JSON structure is malformed or the expected trace style is missing.
    """
    # Ensure the filename ends with .json
    if not filename.lower().endswith(".json"):
        filename += ".json"

    with open(filename, "r", encoding="utf-8") as file:  # Specify UTF-8 encoding for compatibility
        data = json.load(file)

    # Validate JSON structure
    containing_dict = data.get("trace_style")
    if not isinstance(containing_dict, dict):
        raise ValueError("Error: Missing or malformed 'trace_style'.")

    style_name = containing_dict.get("name")
    if not isinstance(style_name, str) or style_name not in containing_dict:
        raise ValueError(f"Error: Expected dictionary '{style_name}' is missing or malformed.")
    trace_style_dict = containing_dict[style_name]

    # Return only the dictionary corresponding to the trace style name
    return trace_style_dict


def apply_layout_style_to_plotly_dict(fig_dict, layout_style_to_apply="default"):
    """
    Applies a predefined layout_style to a fig_dict while preserving non-cosmetic layout fields.

    This function allows applying a custom layout_style (specified by name or as a dictionary) to
    a given fig_dict. It ensures that key non-cosmetic properties (e.g., axis titles, legend titles,
    annotations, and update button labels) are retained even after the style is applied.

    Args:
        fig_dict (dict): A figure dictionary in which the specified or provided layout_style will be applied.
        layout_style_to_apply (str or dict, optional): The name of a layout_style or a layout_style dictionary 
            to apply. Defaults to "default".

    Returns:
        dict: The updated fig_dict with the applied layout_style and preserved layout elements.
    """
    if type(layout_style_to_apply) == type("string"):
        layout_style_to_apply_name = layout_style_to_apply
    else:
        layout_style_to_apply_name = list(layout_style_to_apply.keys())[0]#if it is a dictionary, it will have one key which is its name.
    if (layout_style_to_apply == '') or (str(layout_style_to_apply).lower() == 'none'):
        return fig_dict

    #Hardcoding some cases as ones that will call the default layout, for convenience.
    if (layout_style_to_apply.lower() == "minimalist") or (layout_style_to_apply.lower() == "bold"):
        layout_style_to_apply = "default"


    styles_available = JSONGrapher.styles.layout_styles_library.styles_library


    # Use or get the style specified, or use default if not found
    if isinstance(layout_style_to_apply, dict):
        style_dict = layout_style_to_apply
    else:
        style_dict = styles_available.get(layout_style_to_apply, {})
        if not style_dict:  # Check if it's an empty dictionary
            print(f"Style named '{layout_style_to_apply}' not found with explicit layout dictionary. Using 'default' layout style.")
            style_dict = styles_available.get("default", {})

    # Ensure layout exists in the figure
    fig_dict.setdefault("layout", {})

    # **Extract non-cosmetic fields**
    non_cosmetic_fields = {
        "title.text": fig_dict.get("layout", {}).get("title", {}).get("text", None),
        "xaxis.title.text": fig_dict.get("layout", {}).get("xaxis", {}).get("title", {}).get("text", None),
        "yaxis.title.text": fig_dict.get("layout", {}).get("yaxis", {}).get("title", {}).get("text", None),
        "zaxis.title.text": fig_dict.get("layout", {}).get("zaxis", {}).get("title", {}).get("text", None),
        "legend.title.text": fig_dict.get("layout", {}).get("legend", {}).get("title", {}).get("text", None),
        "annotations.text": [
            annotation.get("text", None) for annotation in fig_dict.get("layout", {}).get("annotations", [])
        ],
        "updatemenus.buttons.label": [
            button.get("label", None) for menu in fig_dict.get("layout", {}).get("updatemenus", [])
            for button in menu.get("buttons", [])
        ],
        "coloraxis.colorbar.title.text": fig_dict.get("layout", {}).get("coloraxis", {}).get("colorbar", {}).get("title", {}).get("text", None),
    }

    # **Apply style dictionary to create a fresh layout object**
    new_layout = style_dict.get("layout", {}).copy()

    # **Restore non-cosmetic fields**
    if non_cosmetic_fields["title.text"]:
        new_layout.setdefault("title", {})["text"] = non_cosmetic_fields["title.text"]

    if non_cosmetic_fields["xaxis.title.text"]:
        new_layout.setdefault("xaxis", {}).setdefault("title", {})["text"] = non_cosmetic_fields["xaxis.title.text"]

    if non_cosmetic_fields["yaxis.title.text"]:
        new_layout.setdefault("yaxis", {}).setdefault("title", {})["text"] = non_cosmetic_fields["yaxis.title.text"]

    if non_cosmetic_fields["zaxis.title.text"]:
        new_layout.setdefault("zaxis", {}).setdefault("title", {})["text"] = non_cosmetic_fields["zaxis.title.text"]

    if non_cosmetic_fields["legend.title.text"]:
        new_layout.setdefault("legend", {}).setdefault("title", {})["text"] = non_cosmetic_fields["legend.title.text"]

    if non_cosmetic_fields["annotations.text"]:
        new_layout["annotations"] = [{"text": text} for text in non_cosmetic_fields["annotations.text"]]

    if non_cosmetic_fields["updatemenus.buttons.label"]:
        new_layout["updatemenus"] = [{"buttons": [{"label": label} for label in non_cosmetic_fields["updatemenus.buttons.label"]]}]

    if non_cosmetic_fields["coloraxis.colorbar.title.text"]:
        new_layout.setdefault("coloraxis", {}).setdefault("colorbar", {})["title"] = {"text": non_cosmetic_fields["coloraxis.colorbar.title.text"]}

    # **Assign the new layout back into the figure dictionary**
    fig_dict["layout"] = new_layout
    #Now update the fig_dict to signify the new layout_style used.
    if "plot_style" not in fig_dict:
        fig_dict["plot_style"] = {}
    fig_dict["plot_style"]["layout_style"] = layout_style_to_apply_name
    return fig_dict

#TODO: This logic should be changed in the future. There should be a separated function to remove formatting
# versus just removing the current setting of "layout_style"
# So the main class function will also be broken into two and/or need to take an optional argument in
def remove_layout_style_from_plotly_dict(fig_dict):
    """
    Removes any layout field formatting from a fig_dict while retaining any essential layout field content.

    This function strips formatting aspects in the layout field from a fig_dict, such as font and background 
    settings, while preserving non-cosmetic fields like axis titles, annotation texts, and interactive labels.

    Args:
        fig_dict (dict): The fig_dict from which layout_style will be removed.

    Returns:
        dict: The cleaned fig_dict with layout_style fields removed but important layout content retained.
    """
    if "layout" in fig_dict:
        style_keys = ["font", "paper_bgcolor", "plot_bgcolor", "gridcolor", "gridwidth", "tickfont", "linewidth"]

        # **Store non-cosmetic fields if present, otherwise assign None**
        non_cosmetic_fields = {
            "title.text": fig_dict.get("layout", {}).get("title", {}).get("text", None),
            "xaxis.title.text": fig_dict.get("layout", {}).get("xaxis", {}).get("title", {}).get("text", None),
            "yaxis.title.text": fig_dict.get("layout", {}).get("yaxis", {}).get("title", {}).get("text", None),
            "zaxis.title.text": fig_dict.get("layout", {}).get("zaxis", {}).get("title", {}).get("text", None),
            "legend.title.text": fig_dict.get("layout", {}).get("legend", {}).get("title", {}).get("text", None),
            "annotations.text": [annotation.get("text", None) for annotation in fig_dict.get("layout", {}).get("annotations", [])],
            "updatemenus.buttons.label": [
                button.get("label", None) for menu in fig_dict.get("layout", {}).get("updatemenus", [])
                for button in menu.get("buttons", [])
            ],
            "coloraxis.colorbar.title.text": fig_dict.get("layout", {}).get("coloraxis", {}).get("colorbar", {}).get("title", {}).get("text", None),
        }

        # Preserve title text while removing font styling
        if "title" in fig_dict["layout"] and isinstance(fig_dict["layout"]["title"], dict):
            fig_dict["layout"]["title"] = {"text": non_cosmetic_fields["title.text"]} if non_cosmetic_fields["title.text"] is not None else {}

        # Preserve axis titles while stripping font styles
        for axis in ["xaxis", "yaxis", "zaxis"]:
            if axis in fig_dict["layout"] and isinstance(fig_dict["layout"][axis], dict):
                if "title" in fig_dict["layout"][axis] and isinstance(fig_dict["layout"][axis]["title"], dict):
                    fig_dict["layout"][axis]["title"] = {"text": non_cosmetic_fields[f"{axis}.title.text"]} if non_cosmetic_fields[f"{axis}.title.text"] is not None else {}

                # Remove style-related attributes but keep axis configurations
                for key in style_keys:
                    fig_dict["layout"][axis].pop(key, None)

        # Preserve legend title text while stripping font styling
        if "legend" in fig_dict["layout"] and isinstance(fig_dict["layout"]["legend"], dict):
            if "title" in fig_dict["layout"]["legend"] and isinstance(fig_dict["layout"]["legend"]["title"], dict):
                fig_dict["layout"]["legend"]["title"] = {"text": non_cosmetic_fields["legend.title.text"]} if non_cosmetic_fields["legend.title.text"] is not None else {}
            fig_dict["layout"]["legend"].pop("font", None)

        # Preserve annotations text while stripping style attributes
        if "annotations" in fig_dict["layout"]:
            fig_dict["layout"]["annotations"] = [
                {"text": text} if text is not None else {} for text in non_cosmetic_fields["annotations.text"]
            ]

        # Preserve update menu labels while stripping styles
        if "updatemenus" in fig_dict["layout"]:
            for menu in fig_dict["layout"]["updatemenus"]:
                for i, button in enumerate(menu.get("buttons", [])):
                    button.clear()
                    if non_cosmetic_fields["updatemenus.buttons.label"][i] is not None:
                        button["label"] = non_cosmetic_fields["updatemenus.buttons.label"][i]

        # Preserve color bar title while stripping styles
        if "coloraxis" in fig_dict["layout"] and "colorbar" in fig_dict["layout"]["coloraxis"]:
            fig_dict["layout"]["coloraxis"]["colorbar"]["title"] = {"text": non_cosmetic_fields["coloraxis.colorbar.title.text"]} if non_cosmetic_fields["coloraxis.colorbar.title.text"] is not None else {}

        # Remove general style settings without clearing layout structure
        for key in style_keys:
            fig_dict["layout"].pop(key, None)

    #If being told to remove the style, should also pop it from fig_dict.
    if "plot_style" in fig_dict:
        if "layout_style" in fig_dict["plot_style"]:
            fig_dict["plot_style"].pop("layout_style")
    return fig_dict

def extract_layout_style_from_fig_dict(fig_dict):
    """
    Extracts a layout_style dictionary from a fig_dict by pulling out the cosmetic formatting layout properties.

    This function pulls visual configuration details—such as fonts, background colors, margins,
    grid lines, tick styling, and legend positioning—from a given fig_dict to construct a layout_style
    dictionary that can be reused or applied elsewhere.

    Args:
        fig_dict (dict): A fig_dict from which layout formatting fields will be extracted.

    Returns:
        dict: A layout_style dictionary capturing the extracted layout formatting.
    """


    # **Extraction Phase** - Collect cosmetic fields if they exist
    layout = fig_dict.get("layout", {})

    # Note: Each assignment below will return None if the corresponding field is missing
    title_font = layout.get("title", {}).get("font")
    title_x = layout.get("title", {}).get("x")
    title_y = layout.get("title", {}).get("y")

    global_font = layout.get("font")
    paper_bgcolor = layout.get("paper_bgcolor")
    plot_bgcolor = layout.get("plot_bgcolor")
    margin = layout.get("margin")

    # Extract x-axis cosmetic fields
    xaxis_title_font = layout.get("xaxis", {}).get("title", {}).get("font")
    xaxis_tickfont = layout.get("xaxis", {}).get("tickfont")
    xaxis_gridcolor = layout.get("xaxis", {}).get("gridcolor")
    xaxis_gridwidth = layout.get("xaxis", {}).get("gridwidth")
    xaxis_zerolinecolor = layout.get("xaxis", {}).get("zerolinecolor")
    xaxis_zerolinewidth = layout.get("xaxis", {}).get("zerolinewidth")
    xaxis_tickangle = layout.get("xaxis", {}).get("tickangle")

    # **Set flag for x-axis extraction**
    xaxis = any([
        xaxis_title_font, xaxis_tickfont, xaxis_gridcolor, xaxis_gridwidth,
        xaxis_zerolinecolor, xaxis_zerolinewidth, xaxis_tickangle
    ])

    # Extract y-axis cosmetic fields
    yaxis_title_font = layout.get("yaxis", {}).get("title", {}).get("font")
    yaxis_tickfont = layout.get("yaxis", {}).get("tickfont")
    yaxis_gridcolor = layout.get("yaxis", {}).get("gridcolor")
    yaxis_gridwidth = layout.get("yaxis", {}).get("gridwidth")
    yaxis_zerolinecolor = layout.get("yaxis", {}).get("zerolinecolor")
    yaxis_zerolinewidth = layout.get("yaxis", {}).get("zerolinewidth")
    yaxis_tickangle = layout.get("yaxis", {}).get("tickangle")

    # **Set flag for y-axis extraction**
    yaxis = any([
        yaxis_title_font, yaxis_tickfont, yaxis_gridcolor, yaxis_gridwidth,
        yaxis_zerolinecolor, yaxis_zerolinewidth, yaxis_tickangle
    ])

    # Extract legend styling
    legend_font = layout.get("legend", {}).get("font")
    legend_x = layout.get("legend", {}).get("x")
    legend_y = layout.get("legend", {}).get("y")

    # **Assignment Phase** - Reconstruct dictionary in a structured manner
    extracted_layout_style = {"layout": {}}

    if title_font or title_x:
        extracted_layout_style["layout"]["title"] = {}
        if title_font:
            extracted_layout_style["layout"]["title"]["font"] = title_font
        if title_x:
            extracted_layout_style["layout"]["title"]["x"] = title_x
        if title_y:
            extracted_layout_style["layout"]["title"]["y"] = title_y

    if global_font:
        extracted_layout_style["layout"]["font"] = global_font

    if paper_bgcolor:
        extracted_layout_style["layout"]["paper_bgcolor"] = paper_bgcolor
    if plot_bgcolor:
        extracted_layout_style["layout"]["plot_bgcolor"] = plot_bgcolor
    if margin:
        extracted_layout_style["layout"]["margin"] = margin

    if xaxis:
        extracted_layout_style["layout"]["xaxis"] = {}
        if xaxis_title_font:
            extracted_layout_style["layout"]["xaxis"]["title"] = {"font": xaxis_title_font}
        if xaxis_tickfont:
            extracted_layout_style["layout"]["xaxis"]["tickfont"] = xaxis_tickfont
        if xaxis_gridcolor:
            extracted_layout_style["layout"]["xaxis"]["gridcolor"] = xaxis_gridcolor
        if xaxis_gridwidth:
            extracted_layout_style["layout"]["xaxis"]["gridwidth"] = xaxis_gridwidth
        if xaxis_zerolinecolor:
            extracted_layout_style["layout"]["xaxis"]["zerolinecolor"] = xaxis_zerolinecolor
        if xaxis_zerolinewidth:
            extracted_layout_style["layout"]["xaxis"]["zerolinewidth"] = xaxis_zerolinewidth
        if xaxis_tickangle:
            extracted_layout_style["layout"]["xaxis"]["tickangle"] = xaxis_tickangle

    if yaxis:
        extracted_layout_style["layout"]["yaxis"] = {}
        if yaxis_title_font:
            extracted_layout_style["layout"]["yaxis"]["title"] = {"font": yaxis_title_font}
        if yaxis_tickfont:
            extracted_layout_style["layout"]["yaxis"]["tickfont"] = yaxis_tickfont
        if yaxis_gridcolor:
            extracted_layout_style["layout"]["yaxis"]["gridcolor"] = yaxis_gridcolor
        if yaxis_gridwidth:
            extracted_layout_style["layout"]["yaxis"]["gridwidth"] = yaxis_gridwidth
        if yaxis_zerolinecolor:
            extracted_layout_style["layout"]["yaxis"]["zerolinecolor"] = yaxis_zerolinecolor
        if yaxis_zerolinewidth:
            extracted_layout_style["layout"]["yaxis"]["zerolinewidth"] = yaxis_zerolinewidth
        if yaxis_tickangle:
            extracted_layout_style["layout"]["yaxis"]["tickangle"] = yaxis_tickangle

    if legend_font or legend_x or legend_y:
        extracted_layout_style["layout"]["legend"] = {}
        if legend_font:
            extracted_layout_style["layout"]["legend"]["font"] = legend_font
        if legend_x:
            extracted_layout_style["layout"]["legend"]["x"] = legend_x
        if legend_y:
            extracted_layout_style["layout"]["legend"]["y"] = legend_y

    return extracted_layout_style

## Start of Section of Code for Styles and Converting between plotly and matplotlib Fig objectss ##

### Start of section of code with functions for extracting and updating x and y ranges of data series ###

def update_implicit_data_series_x_ranges(fig_dict, range_dict):
    """
    Updates the x_range_default values for any implicit data_series a fig_dict.  Specifically,
    those defined by an 'equation' field or by a 'simulate' feid.

    This function modifies the x_range_default field in each data_series field based on 
    the values in a supplied range_dict. The x_range_default field will only be changed
    within the "equation" and "simulate" fields of data_series dictionaries.
    The rest of the fig_dict is unchanged. A new fig_dict is returned.
    Deep copying ensures the original fig_dict remains unaltered.
    This is function is primarily used for updating the x and y axis scales where an equation or simulation
    will be used in order to match the range that other data series span, to create a properly ranged
    implicit data series production for the final plot.

    Args:
        fig_dict (dict): A fig_dict containing one or more data_series entries that may have 'simulate' or 'equation' fields.
        range_dict (dict): Dictionary with optional keys "min_x" and "max_x" specifying global
            x-axis bounds to apply.

    Returns:
        dict: A new fig_dict with updated x_range_default values in applicable data_series, within their 'simulate' or 'equation' fields.

    Notes:
        If "min_x" or "max_x" in range_dict is None, the existing value for it in the data_series dictionary is preserved.
    """
    import copy  # Import inside function to limit scope

    updated_fig_dict = copy.deepcopy(fig_dict)  # Deep copy avoids modifying original data

    min_x = range_dict["min_x"]
    max_x = range_dict["max_x"]

    for data_series in updated_fig_dict.get("data", []):
        if "equation" in data_series:
            equation_info = data_series["equation"]

            # Determine valid values before assignment
            min_x_value = min_x if (min_x is not None) else equation_info.get("x_range_default", [None, None])[0]
            max_x_value = max_x if (max_x is not None) else equation_info.get("x_range_default", [None, None])[1]

            # Assign updated values
            equation_info["x_range_default"] = [min_x_value, max_x_value]
        
        elif "simulate" in data_series:
            simulate_info = data_series["simulate"]

            # Determine valid values before assignment
            min_x_value = min_x if (min_x is not None) else simulate_info.get("x_range_default", [None, None])[0]
            max_x_value = max_x if (max_x is not None) else simulate_info.get("x_range_default", [None, None])[1]

            # Assign updated values
            simulate_info["x_range_default"] = [min_x_value, max_x_value]

    return updated_fig_dict




def get_fig_dict_ranges(fig_dict, skip_equations=False, skip_simulations=False):
    """
    Extracts the x and y ranges for a fig_dict, returning both overall min/max x/y values and per-series min/max x/y values.

    This function examines each data_series in the fig_dict and computes individual and aggregate
    x/y range boundaries. It accounts for simulation or equation series that include x-range
    metadata, as well as raw data series with explicit "x" and "y" lists. Optional arguments
    allow filtering out simulations or equations from consideration for the overall min/max x/y values,
    and will append None values for those per-series range max values.
    This function is for extracting display limits for a plot, not for evaluation limits.
    That is why equation and simulate fields may have None as their limits.

    Args:
        fig_dict (dict): The fig_dict containing data_series from which ranges will be extracted.
        skip_equations (bool, optional): True will give a fig_range that excludes the ranges from equation-based data_series. Defaults to False.
        skip_simulations (bool, optional): True will give a fig_range that excludes the ranges from simulation-based data_series. Defaults to False.

    Returns:
        tuple:
            - fig_dict_ranges (dict): A dictionary with overall ranges and keys of "min_x", "max_x", "min_y", and "max_y".
            - data_series_ranges (dict): A dictionary containing per-series range limits in four lists with dictionary keys
                    of "min_x", "max_x", "min_y", and "max_y". The Indices in the list match the data_series indices,
                    with the indices of skipped data_series being populated with None as their values.
                    

    Notes:
        - If x_range_default or x_range_limits are unavailable, raw x/y values are used instead.
        - The function avoids errors from empty or missing lists by validating content before computing ranges.
    """
    # Initialize final range values to None to ensure assignment
    fig_dict_ranges = {
        "min_x": None,
        "max_x": None,
        "min_y": None,
        "max_y": None
    }

    data_series_ranges = {
        "min_x": [],
        "max_x": [],
        "min_y": [],
        "max_y": []
    }

    for data_series in fig_dict.get("data", []):
        min_x, max_x, min_y, max_y = None, None, None, None  # Initialize extrema as None

        # Determine if the data series contains either "equation" or "simulate"
        if "equation" in data_series:
            if skip_equations:
                implicit_data_series_to_extract_from = None
                # Will Skip processing, but still append None values
            else:
                implicit_data_series_to_extract_from = data_series["equation"]
        
        elif "simulate" in data_series:
            if skip_simulations:
                implicit_data_series_to_extract_from = None
                # Will Skip processing, but still append None values
            else:
                implicit_data_series_to_extract_from = data_series["simulate"]
        
        else:
            implicit_data_series_to_extract_from = None  # No equation or simulation, process x and y normally

        if implicit_data_series_to_extract_from:
            x_range_default = implicit_data_series_to_extract_from.get("x_range_default", [None, None]) 
            x_range_limits = implicit_data_series_to_extract_from.get("x_range_limits", [None, None]) 

            # Assign values, but keep None if missing
            min_x = (x_range_default[0] if (x_range_default[0] is not None) else x_range_limits[0])
            max_x = (x_range_default[1] if (x_range_default[1] is not None) else x_range_limits[1])

        # Ensure "x" key exists AND list is not empty before calling min() or max()
        if (min_x is None) and ("x" in data_series) and (len(data_series["x"]) > 0):  
            valid_x_values = [x for x in data_series["x"] if x is not None]  # Filter out None values
            if valid_x_values:  # Ensure list isn't empty after filtering
                min_x = min(valid_x_values)  

        if (max_x is None) and ("x" in data_series) and (len(data_series["x"]) > 0):  
            valid_x_values = [x for x in data_series["x"] if x is not None]  # Filter out None values
            if valid_x_values:  # Ensure list isn't empty after filtering
                max_x = max(valid_x_values)  

        # Ensure "y" key exists AND list is not empty before calling min() or max()
        if (min_y is None) and ("y" in data_series) and (len(data_series["y"]) > 0):  
            valid_y_values = [y for y in data_series["y"] if y is not None]  # Filter out None values
            if valid_y_values:  # Ensure list isn't empty after filtering
                min_y = min(valid_y_values)  

        if (max_y is None) and ("y" in data_series) and (len(data_series["y"]) > 0):  
            valid_y_values = [y for y in data_series["y"] if y is not None]  # Filter out None values
            if valid_y_values:  # Ensure list isn't empty after filtering
                max_y = max(valid_y_values)  

        # Always add values to the lists, including None if applicable
        data_series_ranges["min_x"].append(min_x)
        data_series_ranges["max_x"].append(max_x)
        data_series_ranges["min_y"].append(min_y)
        data_series_ranges["max_y"].append(max_y)

    # Filter out None values for overall min/max calculations
    valid_min_x_values = [x for x in data_series_ranges["min_x"] if x is not None]
    valid_max_x_values = [x for x in data_series_ranges["max_x"] if x is not None]
    valid_min_y_values = [y for y in data_series_ranges["min_y"] if y is not None]
    valid_max_y_values = [y for y in data_series_ranges["max_y"] if y is not None]

    fig_dict_ranges["min_x"] = min(valid_min_x_values) if valid_min_x_values else None
    fig_dict_ranges["max_x"] = max(valid_max_x_values) if valid_max_x_values else None
    fig_dict_ranges["min_y"] = min(valid_min_y_values) if valid_min_y_values else None
    fig_dict_ranges["max_y"] = max(valid_max_y_values) if valid_max_y_values else None

    return fig_dict_ranges, data_series_ranges


# # Example usage
# fig_dict = {
#     "data": [
#         {"x": [1, 2, 3, 4], "y": [10, 20, 30, 40]},
#         {"x": [5, 6, 7, 8], "y": [50, 60, 70, 80]},
#         {"equation": {
#             "x_range_default": [None, 500],
#             "x_range_limits": [100, 600]
#         }},
#         {"simulate": {
#             "x_range_default": [None, 700],
#             "x_range_limits": [300, 900]
#         }}
#     ]
# }

# fig_dict_ranges, data_series_ranges = get_fig_dict_ranges(fig_dict, skip_equations=True, skip_simulations=True)  # Skips both
# print("Data Series Values:", data_series_ranges)
# print("Extreme Values:", fig_dict_ranges)

### End of section of code with functions for extracting and updating x and y ranges of data series ###


### Start section of code with functions for cleaning fig_dicts for plotly compatibility ###

def update_title_field(fig_dict_or_subdict, depth=1, max_depth=10):
    """
    Checks 'title' fields in a fig_dict and its sub-dictionary to see if they are strings,
    and if they are, then converts them into a dictionary format.

    JSONGrapher already makes title fields as dictionaries.
    This function is to allow JSONGrapher to be take in fields from old plotly records.
    
    This is a past-compatibilty function. Plotly previously allowed strings for title fields,
    but now recommends (or on some cases requires) a dictionary with field of text because
    the dictionary can then include additional formatting.
    
    This function prepares a JSONGrapher fig_dict for compatibility with updated layout formatting
    conventions, where titles must be dictionaries with a 'text' key. The function  traverses nested dictionaries 
    and lists, transforming any title field that is a plain string into the proper dictionary structure.

    Args:
        fig_dict_or_subdict (dict): The fig_dict or any sub-dictionary to be checked and updated recursively.
        depth (int, optional): Current recursive depth, used internally to limit recursion. Defaults to 1.
        max_depth (int, optional): Maximum allowed recursion depth to avoid infinite loops. Defaults to 10.

    Returns:
        dict: The updated dictionary with properly formatted title fields.
    """
    if depth > max_depth or not isinstance(fig_dict_or_subdict, dict):
        return fig_dict_or_subdict
    
    for key, value in fig_dict_or_subdict.items():
        if key == "title" and isinstance(value, str):  #This is for axes labels.
            fig_dict_or_subdict[key] = {"text": value}
        elif isinstance(value, dict):  # Nested dictionary
            fig_dict_or_subdict[key] = update_title_field(value, depth + 1, max_depth)
        elif isinstance(value, list):  # Lists can contain nested dictionaries
            fig_dict_or_subdict[key] = [update_title_field(item, depth + 1, max_depth) if isinstance(item, dict) else item for item in value]
    return fig_dict_or_subdict




def update_superscripts_strings(fig_dict_or_subdict, depth=1, max_depth=10):
    """
    Replaces superscript-like strings in titles and data series names within a fig_dict.

    This function scans through the fig_dict or sub-dictionary recursively, updating all
    display string content where superscripts are found—such as in titles and legend names
    so that superscripts of display strings will appear correctly in Plotly figures.

    Some example inputs and outputs:
    In : x^(2) + y**(-3) = z^(test)	
    Out: x<sup>2</sup> + y<sup>-3</sup> = z<sup>test</sup>
    In : E = mc**(2)	
    Out: E = mc<sup>2</sup>
    In : a^(b) + c**(d)	
    Out: a<sup>b</sup> + c<sup>d</sup>
    In : r^(theta) and s**(x)	
    Out: r<sup>theta</sup> and s<sup>x</sup>
    In : v^(1) + u^(-1)	
    Out: v<sup>1</sup> + u^(-1)

    Args:
        fig_dict_or_subdict (dict): A fig_dict or sub-dictionary to process recursively.
        depth (int, optional): Current recursion level for nested structures. Defaults to 1.
        max_depth (int, optional): Maximum allowed recursion depth. Defaults to 10.

    Returns:
        dict: The updated dictionary with superscript replacements applied where needed.
    """
    if depth > max_depth or not isinstance(fig_dict_or_subdict, dict):
        return fig_dict_or_subdict
    
    for key, value in fig_dict_or_subdict.items():
        if key == "title": #This is for axes labels and graph title.
            if "text" in fig_dict_or_subdict[key]:
                fig_dict_or_subdict[key]["text"] = replace_superscripts(fig_dict_or_subdict[key]["text"])
        if key == "data": #This is for the legend.
            for data_dict in fig_dict_or_subdict[key]:
                if "name" in data_dict:
                    data_dict["name"] = replace_superscripts(data_dict["name"])
        elif isinstance(value, dict):  # Nested dictionary
            fig_dict_or_subdict[key] = update_superscripts_strings(value, depth + 1, max_depth)
        elif isinstance(value, list):  # Lists can contain nested dictionaries
            fig_dict_or_subdict[key] = [update_superscripts_strings(item, depth + 1, max_depth) if isinstance(item, dict) else item for item in value]
    return fig_dict_or_subdict

#The below function was made with the help of copilot.
def replace_superscripts(input_string):
    """
    Takes a string, finds superscripts denoted symbolically (** or ^), and replaces the
    symbolic superscript syntax with tagged markup syntax (<sup> </sup>)

    Some example inputs and outputs:
    In : x^(2) + y**(-3) = z^(test)	
    Out: x<sup>2</sup> + y<sup>-3</sup> = z<sup>test</sup>
    In : E = mc**(2)	
    Out: E = mc<sup>2</sup>
    In : a^(b) + c**(d)	
    Out: a<sup>b</sup> + c<sup>d</sup>
    In : r^(theta) and s**(x)	
    Out: r<sup>theta</sup> and s<sup>x</sup>
    In : v^(1) + u^(-1)	
    Out: v<sup>1</sup> + u^(-1)

    Args:
        input_string (str): A string possibly including superscripts denoted by ** or ^
       
    Returns:
        str: A string with superscript symbolic notation replaced with tagged markup (<sup> </sup>) notation.
    """
    #Example usage: print(replace_superscripts("x^(2) + y**(-3) = z^(test)"))
    import re
    # Step 1: Wrap superscript expressions in <sup> tags
    output_string = re.sub(r'\^\((.*?)\)|\*\*\((.*?)\)', 
                           lambda m: f"<sup>{m.group(1) or m.group(2)}</sup>", 
                           input_string)
    # Step 2: Remove parentheses if the content is only digits
    output_string = re.sub(r'<sup>\((\d+)\)</sup>', r'<sup>\1</sup>', output_string)
    # Step 3: Remove parentheses if the content is a negative number (- followed by digits)
    # Step 4: Remove parentheses if the superscript is a single letter
    output_string = re.sub(r'<sup>\((\w)\)</sup>', r'<sup>\1</sup>', output_string)
    output_string = re.sub(r'<sup>\(-(\d+)\)</sup>', r'<sup>-\1</sup>', output_string)
    return output_string


def convert_to_3d_layout(layout):
    """
    Converts a standard JSONGrapher layout_dict into the format needed for a plotly 3D layout_dict by nesting axis fields under the 'scene' key.

    This function reorganizes xaxis, yaxis, and zaxis fields from a standard JSONGrapher layout_dict
    into a Plotly 3D layout_dict by moving axes fields into the 'scene' field, as required for
    the current plotly schema for 3D plots. A deep copy of the layout_dict is used so the original layout_dict remains untouched.
    This way of doing things is so JSONGrapher layout_dicts are consistent across 2D and 3D plots 
    whereas Plotly does things differently for 3D plots, so this function converts a
    standard JSONGrapher layout_dict into what is expected for Plotly 3D plots.
    
    Args:
        layout (dict): A  standard JSONGrapher layout_dict, typically extracted from a fig_dict.

    Returns:
        dict: A Plotly 3D layout_dict with axes fields moved to 'scene' field.
    """
    import copy
    # Create a deep copy to avoid modifying the original layout
    new_layout = copy.deepcopy(layout)

    # Add the axis fields inside `scene` first
    scene = new_layout.setdefault("scene", {}) #Create a new dict if not present, otherwise use existing one.
    scene["xaxis"] = layout.get("xaxis", {})
    scene["yaxis"] = layout.get("yaxis", {})
    scene["zaxis"] = layout.get("zaxis", {})

    # Remove the original axis fields from the top-level layout
    new_layout.pop("xaxis", None)
    new_layout.pop("yaxis", None)
    new_layout.pop("zaxis", None)

    return new_layout

    #A bubble plot uses z data, but that data is then
    #moved into the size field and the z field must be removed.

def remove_bubble_fields(fig_dict):
    """
    Removes JSONGrapher bubble plot creation fields to make a JSONGrapher fig_dict Plotly compatible.

    This function iterates over data_series entries in the fig_dict and removes 'bubble_size',
    and 'max_bubble_size' fields from entries marked as bubble plots. 
    
    Args:
        fig_dict (dict): A fig_dict potentially containing JSONGrapher bubble plot data_series.

    Returns:
        dict: The updated fig_dict with JSONGrapher bubble plot creation fields removed for Plotly graphing compatibility.
    """
    #This code will modify the data_series inside the fig_dict, directly.
    bubble_found = False #initialize with false case.
    for data_series in fig_dict["data"]:
        trace_style = data_series.get("trace_style") #trace_style will be None of the key is not present.

        if isinstance(trace_style, str):
            #If the style is just "bubble" (not explicitly 2D or 3D), default to bubble2d for backward compatibility
            if ("bubble" in trace_style) and ("bubble3d" not in trace_style) and ("bubble2d" not in trace_style):
                trace_style = trace_style.replace("bubble", "bubble2d") 
            if ("bubble" in trace_style.lower()) or ("max_bubble_size" in data_series):
                bubble_found = True
            if bubble_found is True:
                if "bubble2d" in trace_style.lower(): #pop the z variable if it's a bubble2d.
                    if "z" in data_series:
                        data_series.pop("z")
                    if "z_points" in data_series:
                        data_series.pop("z_points")
                if "max_bubble_size" in data_series:
                    data_series.pop("max_bubble_size")
                if "bubble_sizes" in data_series:
                    # Now, need to check if the bubble_size is a variable that should be deleted.
                    # That will be if it is a string, and also not a standard variable. 
                    if isinstance(data_series["bubble_sizes"], str):
                        bubble_sizes_variable_name = data_series["bubble_sizes"]
                        # For bubble2d case, will remove anything that is not x or y.
                        if "bubble2d" in trace_style.lower():
                            if bubble_sizes_variable_name not in ("x", "y"):
                                data_series.pop(bubble_sizes_variable_name, None)
                        if "bubble3d" in trace_style.lower():
                            if bubble_sizes_variable_name not in ("x", "y", "z"):
                                data_series.pop(bubble_sizes_variable_name, None)
                    # next, remove bubble_sizes since it's not needed anymore and should be removed.
                    data_series.pop("bubble_sizes")
                # need to remove "zaxis" if making a bubble2d.
                if "bubble2d" in trace_style.lower():
                    if "zaxis" in fig_dict["layout"]:
                        fig_dict["layout"].pop("zaxis")
    return fig_dict

def update_3d_axes(fig_dict):
    """
    Converts a JSONGrapher 3D graph fig_dict to be compatible with Plotly 3D plotting. Modifies layout_dict and data_series dictionaries.

    This function converts the layout of a fig_dict to a Plotly 3D format by nesting axis fields under 'scene',
    and also adjusts data_series entries as needed, based on their 3D plot types. For scatter3d and mesh3d traces,
    any 'z_matrix' fields are removed. For surface plots, 'z' is removed if 'z_matrix' is present and
    a notice is printed indicating the need for further transformation.

    Args:
        fig_dict (dict): A fig_dict that may contain JSONGrapher format denoting 3D axes and/or trace_style fields.

    Returns:
        dict: The updated fig_dict prepared for Plotly 3D rendering.
    """
    if "zaxis" in fig_dict["layout"]:
        fig_dict['layout'] = convert_to_3d_layout(fig_dict['layout'])
        for data_series_index, data_series in enumerate(fig_dict["data"]):
            if data_series["type"] == "scatter3d":
                if "z_matrix" in data_series: #for this one, we don't want the z_matrix.
                    data_series.pop("z_matrix")
            if data_series["type"] == "mesh3d":
                if "z_matrix" in data_series: #for this one, we don't want the z_matrix.
                    data_series.pop("z_matrix")
            if data_series["type"] == "surface":
                if "z_matrix" in data_series: #for this one, we want the z_matrix so we pop z if we have the z_matrix..
                    data_series.pop("z")
                print(" The Surface type of 3D plot has not been implemented yet. It requires replacing z with the z_matrix after the equation has been evaluated.")
    return fig_dict

def remove_extra_information_field(fig_dict, depth=1, max_depth=10):
    """
    Recursively removes 'extraInformation' or 'extra_information' fields from a fig_dict for Plotly plotting compatibility.

    This function traverses a fig_dict or sub-dictionary structure to eliminate keys related to extra metadata
    that are not supported by current Plotly layout format expectations. It supports deeply nested dictionaries and lists.

    Args:
        fig_dict (dict): A fig_dict or nested sub-dictionary.
        depth (int, optional): The current recursion depth during traversal. Defaults to 1.
        max_depth (int, optional): Maximum depth to avoid infinite recursion. Defaults to 10.

    Returns:
        dict: The updated dictionary with all 'extraInformation' fields removed.
    """
    if depth > max_depth or not isinstance(fig_dict, dict):
        return fig_dict

    # Use a copy of the dictionary keys to safely modify the dictionary during iteration
    for key in list(fig_dict.keys()):
        if key == ("extraInformation" or "extra_information"):
            del fig_dict[key]  # Remove the field
        elif isinstance(fig_dict[key], dict):  # Nested dictionary
            fig_dict[key] = remove_extra_information_field(fig_dict[key], depth + 1, max_depth)
        elif isinstance(fig_dict[key], list):  # Lists can contain nested dictionaries
            fig_dict[key] = [
                remove_extra_information_field(item, depth + 1, max_depth) if isinstance(item, dict) else item for item in fig_dict[key]
            ]
    
    return fig_dict
    

def remove_nested_comments(data, top_level=True):
    """
    Removes all nested 'comments' fields from a fig_dict while preserving top-level comments.

    This function recursively traverses a fig_dict or sub-dictionary, removing any 'comments'
    entries found below the top level. This ensures compatibility with layout formats that
    do not support metadata fields in nested locations.

    Args:
        data (dict): The fig_dict or sub-dictionary to process.
        top_level (bool, optional): Indicates whether the current recursion level is the top level.
            Defaults to True.

    Returns:
        dict: The updated dictionary with nested 'comments' fields removed.
    """
    if not isinstance(data, dict):
        return data
    # Process nested structures
    for key in list(data.keys()):
        if isinstance(data[key], dict):  # Nested dictionary
            data[key] = remove_nested_comments(data[key], top_level=False)
        elif isinstance(data[key], list):  # Lists can contain nested dictionaries
            data[key] = [
                remove_nested_comments(item, top_level=False) if isinstance(item, dict) else item for item in data[key]
            ]
    # Only remove 'comments' if not at the top level
    if not top_level:
        data = {k: v for k, v in data.items() if k != "comments"}
    return data

def remove_simulate_field(json_fig_dict):
    """
    Removes all 'simulate' fields from the data_series in a fig_dict.

    This function iterates through each entry in the fig_dict's 'data' list and deletes
    the 'simulate' field if it exists. This prepares the fig_dict for use cases where
    simulation metadata is unnecessary or unsupported.

    Args:
        json_fig_dict (dict): A fig_dict containing a list of data_series entries.

    Returns:
        dict: The updated fig_dict with 'simulate' fields removed from each data_series.
    """
    data_dicts_list = json_fig_dict['data']
    for data_dict in data_dicts_list:
        data_dict.pop('simulate', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
    json_fig_dict['data'] = data_dicts_list #this line shouldn't be necessary, but including it for clarity and carefulness.
    return json_fig_dict

def remove_equation_field(json_fig_dict):
    """
    Removes all 'equation' fields from the data_series in a fig_dict.

    This function scans through each item in the 'data' list of a fig_dict and deletes the
    'equation' field if it is present. This is useful for stripping out symbolic definitions
    or expression metadata for use cases where the equation metadata is unnecessary or unsupported.
    
    Args:
        json_fig_dict (dict): A fig_dict containing a list of data_series entries.

    Returns:
        dict: The updated fig_dict with 'equation' fields removed from each data_series.
    """
    data_dicts_list = json_fig_dict['data']
    for data_dict in data_dicts_list:
        data_dict.pop('equation', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
    json_fig_dict['data'] = data_dicts_list #this line shouldn't be necessary, but including it for clarity and carefulness.
    return json_fig_dict

def remove_trace_style_field(json_fig_dict):
    """
    Removes 'trace_style' and 'tracetype' fields from all data_series entries in a fig_dict.

    This function iterates through the 'data' list of a fig_dict and deletes styling hints such as 
    'trace_style' and 'tracetype' from each data_series. This is useful for stripping out internal 
    metadata before serialization or external use.

    Args:
        json_fig_dict (dict): A fig_dict containing a list of data_series entries.

    Returns:
        dict: The updated fig_dict with trace style metadata removed from all data_series.
    """
    data_dicts_list = json_fig_dict['data']
    for data_dict in data_dicts_list:
        data_dict.pop('trace_style', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
        data_dict.pop('tracetype', None) #Some people recommend using pop over if/del as safer. Both ways should work under normal circumstances.
    json_fig_dict['data'] = data_dicts_list #this line shouldn't be necessary, but including it for clarity and carefulness.
    return json_fig_dict

def remove_custom_units_chevrons(json_fig_dict):
    """
    Removes angle bracket characters ('<' and '>') from axis title text fields in a fig_dict.

    This function scans the xaxis, yaxis, and zaxis title text strings in the layout of a fig_dict
    and removes any chevrons that may exist. It is useful for cleaning up units or labels that
    were enclosed in angle brackets for processing purposes.

    Args:
        json_fig_dict (dict): A fig_dict containing axis title text to sanitize.

    Returns:
        dict: The updated fig_dict with angle brackets removed from axis title labels.
    """
    try:
        json_fig_dict['layout']['xaxis']['title']['text'] = json_fig_dict['layout']['xaxis']['title']['text'].replace('<','').replace('>','')
    except KeyError:
        pass
    try:
        json_fig_dict['layout']['yaxis']['title']['text'] = json_fig_dict['layout']['yaxis']['title']['text'].replace('<','').replace('>','')
    except KeyError:
        pass
    try:
        json_fig_dict['layout']['zaxis']['title']['text'] = json_fig_dict['layout']['zaxis']['title']['text'].replace('<','').replace('>','')
    except KeyError:
        pass
    return json_fig_dict

def clean_json_fig_dict(json_fig_dict, fields_to_update=None):
    """
    Cleans and updates a fig_dict by applying selected transformations for Plotly compatibility.

    This function allows selective sanitization of a fig_dict by applying a set of transformations 
    defined in fields_to_update. It prepares a JSONGrapher-compatible dictionary for use with 
    Plotly figure objects by modifying or removing fields such as titles, equations, simulation 
    definitions, custom units, and unused styling metadata.

    Args:
        json_fig_dict (dict): The original fig_dict containing layout and data_series.
        fields_to_update (list, optional): A list of update operations to apply. Defaults to 
            ["title_field", "extraInformation", "nested_comments"].

    Returns:
        dict: The cleaned and optionally transformed fig_dict.

    Supported options in fields_to_update:
        - "title_field": Updates title fields to dictionary format.
        - "extraInformation": Removes extra metadata fields.
        - "nested_comments": Removes non-top-level comments.
        - "simulate": Removes simulate fields from data_series.
        - "equation": Removes equation fields from data_series.
        - "custom_units_chevrons": Removes angle brackets in axis titles.
        - "bubble": Strips bubble-specific fields and removes zaxis.
        - "trace_style": Removes internal style/tracetype metadata.
        - "3d_axes": Updates layout and data_series for 3D plotting.
        - "superscripts": Replaces superscript strings in titles and labels.
        - "offset": Removes the offset field from the layout field.
    """
    if fields_to_update is None:  # should not initialize mutable objects in arguments line, so doing here.
        fields_to_update = ["title_field", "extraInformation", "nested_comments"]
    fig_dict = json_fig_dict
    #unmodified_data = copy.deepcopy(data)
    if "title_field" in fields_to_update:
        fig_dict = update_title_field(fig_dict)
    if "extraInformation" in fields_to_update:
        fig_dict = remove_extra_information_field(fig_dict)
    if "nested_comments" in fields_to_update:
        fig_dict = remove_nested_comments(fig_dict)
    if "simulate" in fields_to_update:
        fig_dict = remove_simulate_field(fig_dict)
    if "equation" in fields_to_update:
        fig_dict = remove_equation_field(fig_dict)
    if "custom_units_chevrons" in fields_to_update:
        fig_dict = remove_custom_units_chevrons(fig_dict)
    if "bubble" in fields_to_update: #must be updated before trace_style is removed.
        fig_dict = remove_bubble_fields(fig_dict)
    if "trace_style" in fields_to_update:
        fig_dict = remove_trace_style_field(fig_dict)
    if "3d_axes" in fields_to_update: #This is for 3D plots
        fig_dict = update_3d_axes(fig_dict)
    if "superscripts" in fields_to_update:
        fig_dict = update_superscripts_strings(fig_dict)

    return fig_dict

### End section of code with functions for cleaning fig_dicts for plotly compatibility ###

### Beginning of section of file that has functions for "simulate" and "equation" fields, to evaluate equations and call external javascript simulators, as well as support functions ###

local_python_functions_dictionary = {} #This is a global variable that works with the "simulate" feature and lets users call python functions for data generation.

def run_js_simulation(javascript_simulator_url, simulator_input_json_dict, verbose = False):
    """
    Runs a JavaScript-based simulation by downloading and executing a js file with a simulate function from a URL.

    This function fetches a JavaScript file containing a simulate function, appends a module export,
    and invokes it using Node.js with the provided simulation input dictionary. The resulting simulation output,
    if properly formatted, is returned as parsed JSON.

    # Example inputs
    javascript_simulator_url = "https://github.com/AdityaSavara/JSONGrapherExamples/blob/main/ExampleSimulators/Langmuir_Isotherm.js"
    simulator_input_json_dict = {
        "simulate": {
            "K_eq": None,
            "sigma_max": "1.0267670459667 (mol/kg)",
            "k_ads": "200 (1/(bar * s))",
            "k_des": "100 (1/s)"
        }
    }

    Args:
        javascript_simulator_url (str): URL pointing to the raw JavaScript file containing a 'simulate' function.
        simulator_input_json_dict (dict): Dictionary of inputs to pass to the simulate function.
        verbose (bool, optional): If True, prints standard output and error streams from Node.js execution. Defaults to False.

    Returns:
        dict or None: Parsed dictionary output from the simulation, or None if an error occurred.
    """
    import requests
    import subprocess
    #import json
    import os

    # Convert to raw GitHub URL only if "raw" is not in the original URL
    # For example, the first link below gets converted to the second one.
    # https://github.com/AdityaSavara/JSONGrapherExamples/blob/main/ExampleSimulators/Langmuir_Isotherm.js
    # https://raw.githubusercontent.com/AdityaSavara/JSONGrapherExamples/main/ExampleSimulators/Langmuir_Isotherm.js    
    
    if "raw" not in javascript_simulator_url:
        javascript_simulator_url = convert_to_raw_github_url(javascript_simulator_url)

    # Extract filename from URL
    js_filename = os.path.basename(javascript_simulator_url)

    # Download the JavaScript file
    response = requests.get(javascript_simulator_url, timeout=300)

    if response.status_code == 200:
        with open(js_filename, "w", encoding="utf-8") as file:  # Specify UTF-8 encoding for compatibility
            file.write(response.text)

        # Append the export statement to the JavaScript file
        with open(js_filename, "a", encoding="utf-8") as file:  # Specify UTF-8 encoding for compatibility
            file.write("\nmodule.exports = { simulate };")

        # Convert input dictionary to a JSON string
        input_json_str = json.dumps(simulator_input_json_dict)

        # Prepare JavaScript command for execution
        js_command = f"""
        const simulator = require('./{js_filename}');
        console.log(JSON.stringify(simulator.simulate({input_json_str})));
        """

        result = subprocess.run(["node", "-e", js_command], capture_output=True, text=True, check=True)

        # Print output and errors if verbose
        if verbose:
            print("Raw JavaScript Output:", result.stdout)
            print("Node.js Errors:", result.stderr)

        # Parse JSON if valid
        if result.stdout.strip():
            try:
                data_dict_with_simulation = json.loads(result.stdout) #This is the normal case.
                return data_dict_with_simulation
            except json.JSONDecodeError:
                print("Error: JavaScript output is not valid JSON.")
                return None
    else:
        print(f"Error: Unable to fetch JavaScript file. Status code {response.status_code}")
        return None

def convert_to_raw_github_url(url):
    """
    Checks for and converts any GitHub file URLs to its raw content URL format for direct access to file contents. Non Github urls are unchanged.

    This utility rewrites standard GitHub URLs (with or without 'blob') into their raw content
    equivalents on raw.githubusercontent.com. It preserves the full file path and is used as a 
    helper for code that dynamically executes JavaScript files from GitHub.

    Args:
        url (str): A URL possibly pointing to a GitHub file.

    Returns:
        str: An unchanged url if not a Github url, or a raw GitHub URL suitable for direct content download.
    """
    from urllib.parse import urlparse
    parsed_url = urlparse(url)

    # If the URL is already a raw GitHub link, return it unchanged
    if "raw.githubusercontent.com" in parsed_url.netloc:
        return url

    path_parts = parsed_url.path.strip("/").split("/")

    # Ensure it's a valid GitHub file URL
    if "github.com" in parsed_url.netloc and len(path_parts) >= 4:
        if path_parts[2] == "blob":  
            # If the URL contains "blob", adjust extraction
            user, repo, branch = path_parts[:2] + [path_parts[3]]
            file_path = "/".join(path_parts[4:])  # Keep full file path including filename
        else:
            # Standard GitHub file URL (without "blob")
            user, repo, branch = path_parts[:3]
            file_path = "/".join(path_parts[3:])  # Keep full file path including filename

        return f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"

    return url  # Return unchanged if not a GitHub file URL

#This function takes in a data_series_dict object and then
#calls an external python or javascript simulation if needed
#Then fills the data_series dict with the simulated data.
#This function is not intended to be called by the regular user
#because it returns extra fields that need to be parsed out.
#and because it does not do unit conversions as needed after the simulation resultss are returned.
def simulate_data_series(data_series_dict, simulator_link='', verbose=False):
    """
    Runs a simulation for a data_series_dict using either a local Python function or a remote JavaScript simulator.

    This function determines which simulator to invoke—based on the provided simulator_link or the data_series_dict["simulate"]["model"]  
    field, and calls the appropriate method to generate simulation results. It can handle both local Python-based
    simulation functions and compatible remote JavaScript simulate modules. Intended for internal use, this function 
    may return additional fields that require further parsing and does not perform post-simulation unit conversions.

    Args:
        data_series_dict (dict): Dictionary describing a single data_series, including simulation parameters.
        simulator_link (str, optional): Either the name of a local Python simulator or a URL to a JS simulator.
            If not provided, this function extracts the value from data_series_dict["simulate"]["model"] and follows that.
        verbose (bool, optional): Whether to print raw simulation output and error details. Defaults to False.

    Returns:
        dict or None: The simulated data_series dictionary or None if an error occurred during execution.
    """
    if simulator_link == '':
        simulator_link = data_series_dict["simulate"]["model"]  
    if simulator_link == "local_python": #this is the local python case.
        #Here, I haev split up the lines of code more than needed so that the logic is easy to follow.
        simulation_function_label = data_series_dict["simulate"]["simulation_function_label"]
        simulation_function = local_python_functions_dictionary[simulation_function_label] 
        simulation_return = simulation_function(data_series_dict) 
        if "data" in simulation_return: #the simulation return should have the data_series_dict in another dictionary.
            simulation_result = simulation_return["data"]
        else: #if there is no "data" field, we will assume that only the data_series_dict has been returned.
            simulation_result = simulation_return
        return simulation_result
    else:
        try:
            simulation_return = run_js_simulation(simulator_link, data_series_dict, verbose=verbose)
            if isinstance(simulation_return, dict) and "error" in simulation_return: # Check for errors in the returned data
                print(f"Simulation failed: {simulation_return.get('error_message', 'Unknown error')}")
                print(simulation_return)
                return None
            return simulation_return.get("data", None) # Returns data, but will return "None" if data does not exist.
        except Exception as e: # This is so VS code pylint does not flag this line. pylint: disable=broad-except
            print(f"Exception occurred in simulate_data_series function of JSONRecordCreator.py: {e}")
            return None

#Function that goes through a fig_dict data series and simulates each data series as needed.
#If the simulated data returned has "x_label" and/or "y_label" with units, those will be used to scale the data, then will be removed.
def simulate_as_needed_in_fig_dict(fig_dict, simulator_link='', verbose=False):
    """
    Iterates through the data_series in a fig_dict and performs simulation for each as needed.

    This function checks each data_series in the fig_dict and applies simulation using either
    a specified simulator_link or the model defined within each entry. If the simulation result
    includes 'x_label' or 'y_label' with units, those are used to scale the data before removing 
    the label fields.

    Args:
        fig_dict (dict): A fig_dict containing a 'data' list with data_series dictionary entries to simulate.
        simulator_link (str, optional): An override simulator link or label to apply across all series.
            Defaults to an empty string, in which case this function checks each data_series dictionary to determine the simulator to use.
        verbose (bool, optional): Whether to log/output updates and warnings during the simulation process. Defaults to False.

    Returns:
        dict: The updated fig_dict with simulated results entered into those data_series dictionary fields.
    """
    data_dicts_list = fig_dict['data']    
    for data_dict_index in range(len(data_dicts_list)):
        fig_dict = simulate_specific_data_series_by_index(fig_dict, data_dict_index, simulator_link=simulator_link, verbose=verbose)
    return fig_dict

#Function that takes fig_dict and dataseries index and simulates if needed. Also performs unit conversions as needed.
#If the simulated data returned has "x_label" and/or "y_label" with units, those will be used to scale the data, then will be removed.
def simulate_specific_data_series_by_index(fig_dict, data_series_index, simulator_link='', verbose=False):
    """
    Simulates a specific data_series within a fig_dict and applies unit scaling if required.

    This function targets a single data_series by index in the fig_dict, performs simulation
    using either a specified or embedded simulator, and scales the results to match the units
    found in the fig_dict layout. If x_label or y_label with units are present in the simulation
    output, corresponding unit conversions are applied to the data and those fields are removed.

    Args:
        fig_dict (dict): The figure dictionary containing a list of data_series.
        data_series_index (int): Index of the data_series to simulate and update.
        simulator_link (str, optional): Path or URL to the simulator to use. If empty, 
            the simulator is inferred from the data_series entry. Defaults to ''.
        verbose (bool, optional): If True, prints diagnostic details including scaling ratios. Defaults to False.

    Returns:
        dict: The updated fig_dict with any simulated results entered into the appropriate data_series dictionary.
    """
    data_dicts_list = fig_dict['data']
    data_dict_index = data_series_index
    data_dict = data_dicts_list[data_dict_index]
    if 'simulate' in data_dict:
        data_dict_filled = simulate_data_series(data_dict, simulator_link=simulator_link, verbose=verbose)
        # Check if unit scaling is needed
        if ("x_label" in data_dict_filled) or ("y_label" in data_dict_filled):
            #first, get the units that are in the layout of fig_dict so we know what to convert to.
            existing_record_x_label = fig_dict["layout"]["xaxis"]["title"]["text"]
            existing_record_y_label = fig_dict["layout"]["yaxis"]["title"]["text"]
            # Extract units  from the simulation output.
            existing_record_x_units = separate_label_text_from_units(existing_record_x_label).get("units", "")
            existing_record_y_units = separate_label_text_from_units(existing_record_y_label).get("units", "")
            simulated_data_series_x_units = separate_label_text_from_units(data_dict_filled.get('x_label', '')).get("units", "")
            simulated_data_series_y_units = separate_label_text_from_units(data_dict_filled.get('y_label', '')).get("units", "")
            # Compute unit scaling ratios
            x_units_ratio = get_units_scaling_ratio(simulated_data_series_x_units, existing_record_x_units) if simulated_data_series_x_units and existing_record_x_units else 1
            y_units_ratio = get_units_scaling_ratio(simulated_data_series_y_units, existing_record_y_units) if simulated_data_series_y_units and existing_record_y_units else 1
            # Apply scaling to the data series
            scale_dataseries_dict(data_dict_filled, num_to_scale_x_values_by=x_units_ratio, num_to_scale_y_values_by=y_units_ratio)
            #Verbose logging for debugging
            if verbose:
                print(f"Scaling X values by: {x_units_ratio}, Scaling Y values by: {y_units_ratio}")
            #Now need to remove the "x_label" and "y_label" to be compatible with plotly.
            data_dict_filled.pop("x_label", None)
            data_dict_filled.pop("y_label", None)
        # Update the figure dictionary
        data_dicts_list[data_dict_index] = data_dict_filled
    fig_dict['data'] = data_dicts_list
    return fig_dict

def evaluate_equations_as_needed_in_fig_dict(fig_dict):
    """
    Evaluates and updates any equation-based data_series entries in a fig_dict.

    This function scans the fig_dict for data_series entries that contain an 'equation' field.
    For each such entry, it invokes the appropriate equation evaluation logic to generate
    x/y data, replacing or augmenting the original data_series with the computed results.

    Args:
        fig_dict (dict): A figure dictionary potentially containing equation-based data_series.

    Returns:
        dict: The updated fig_dict with equation data_series evaluated and populated with data.
    """
    data_dicts_list = fig_dict['data']
    for data_dict_index, data_dict in enumerate(data_dicts_list):
        if 'equation' in data_dict:
            fig_dict = evaluate_equation_for_data_series_by_index(fig_dict, data_dict_index)
    return fig_dict

#TODO: Should add z units ratio scaling here (just to change units when merging records). Should do the same for the simulate_specific_data_series_by_index function.
def evaluate_equation_for_data_series_by_index(fig_dict, data_series_index, verbose="auto"):   
    """
    Evaluates a symbolic equation for the data_series at the specified index of the provided fig_dict and performs units conversion / scaling as needed.

    This function targets an indexed data_series entry with an 'equation' field and uses an external 
    equation engine to evaluate and populate x/y/z data values. If axis labels include units, the values 
    are converted/scaled to match the units defined in the fig_dict layout. The function also assigns default 
    trace types based on the dimensionality of the evaluated data.

    Args:
        fig_dict (dict): A fig_dict containing a list of data_series and corresponding layout metadata.
        data_series_index (int): The index of the data_series containing the equation to evaluate.
        verbose (str or bool, optional): Controls verbosity of the evaluation engine. Defaults to "auto".

    Returns:
        dict: The updated fig_dict with the specified data_series evaluated and replaced with numeric values.
    """
    try:
        # Attempt to import from the json_equationer package
        import json_equationer.equation_creator as equation_creator
    except ImportError:
        try:
             # Fallback: attempt local import
            from . import equation_creator
        except ImportError as exc:
             # Log the failure and handle gracefully
            print(f"Failed to import equation_creator: {exc}")
    import copy
    data_dicts_list = fig_dict['data']
    data_dict = data_dicts_list[data_series_index]
    if 'equation' in data_dict:
        equation_object = equation_creator.Equation(data_dict['equation'])
        if verbose == "auto":
            equation_dict_evaluated = equation_object.evaluate_equation()
        else:
            equation_dict_evaluated = equation_object.evaluate_equation(verbose=verbose)
        if "graphical_dimensionality" in equation_dict_evaluated:
            graphical_dimensionality = equation_dict_evaluated["graphical_dimensionality"]
        else:
            graphical_dimensionality = 2
        data_dict_filled = copy.deepcopy(data_dict)
        data_dict_filled['equation'] = equation_dict_evaluated
        data_dict_filled['x_label'] = data_dict_filled['equation']['x_variable'] 
        data_dict_filled['y_label'] = data_dict_filled['equation']['y_variable'] 
        data_dict_filled['x'] = list(equation_dict_evaluated['x_points'])
        data_dict_filled['y'] = list(equation_dict_evaluated['y_points'])
        data_dict_filled['x_units'] = equation_dict_evaluated['x_units']
        data_dict_filled['y_units'] = equation_dict_evaluated['y_units']
        if graphical_dimensionality == 3:
            data_dict_filled['z_label'] = data_dict_filled['equation']['z_variable'] 
            data_dict_filled['z'] = list(equation_dict_evaluated['z_points'])
            data_dict_filled['z_units'] = equation_dict_evaluated['z_units']
        #data_dict_filled may include "x_label" and/or "y_label". If it does, we'll need to check about scaling units.
        if (("x_label" in data_dict_filled) or ("y_label" in data_dict_filled)) or ("z_label" in data_dict_filled):
            #first, get the units that are in the layout of fig_dict so we know what to convert to.
            existing_record_x_label = fig_dict["layout"]["xaxis"]["title"]["text"] #this is a dictionary.
            existing_record_y_label = fig_dict["layout"]["yaxis"]["title"]["text"] #this is a dictionary.
            existing_record_x_units = separate_label_text_from_units(existing_record_x_label)["units"]
            existing_record_y_units = separate_label_text_from_units(existing_record_y_label)["units"]
            existing_record_z_label = '' #initializing so it is not undefined.
            if "z_label" in data_dict_filled:
                existing_record_z_label = fig_dict["layout"]["zaxis"]["title"]["text"] #this is a dictionary.
                existing_record_z_units = separate_label_text_from_units(existing_record_z_label)["units"]
            if (existing_record_x_units == '') and (existing_record_y_units == '') and (existing_record_z_units == ''): #skip scaling if there are no units.
                pass
            else: #If we will be scaling...
                #now, get the units from the evaluated equation output.
                simulated_data_series_x_units = data_dict_filled['x_units']
                simulated_data_series_y_units = data_dict_filled['y_units']
                x_units_ratio = get_units_scaling_ratio(existing_record_x_units, simulated_data_series_x_units)
                y_units_ratio = get_units_scaling_ratio(existing_record_y_units, simulated_data_series_y_units)
                z_units_ratio = 1 #initializing
                if "z_label" in data_dict_filled:
                    simulated_data_series_z_units = data_dict_filled['z_units']
                    z_units_ratio = get_units_scaling_ratio(existing_record_z_units, simulated_data_series_z_units)
                #We scale the dataseries, which really should be a function.
                scale_dataseries_dict(data_dict_filled, num_to_scale_x_values_by = x_units_ratio, num_to_scale_y_values_by = y_units_ratio, num_to_scale_z_values_by = z_units_ratio)
            #Now need to remove the "x_label" and "y_label" to be compatible with plotly.
            data_dict_filled.pop("x_label", None)
            data_dict_filled.pop("y_label", None)
            data_dict_filled.pop("x_units", None)
            data_dict_filled.pop("y_units", None)
            if "z_label" in data_dict_filled:
                data_dict_filled.pop("z_label", None)
                data_dict_filled.pop("z_units", None)
        if "type" not in data_dict:
            if graphical_dimensionality == 2:
                data_dict_filled['type'] = 'spline'
            elif graphical_dimensionality == 3:
                data_dict_filled['type'] = 'mesh3d'
        data_dicts_list[data_series_index] = data_dict_filled
    fig_dict['data'] = data_dicts_list
    return fig_dict


def update_implicit_data_series_data(target_fig_dict, source_fig_dict, parallel_structure=True, modify_target_directly = False):
    """
    Synchronizes x, y, and z data for implicit data series between two fig_dicts.

    This function transfers numerical data values from a source fig_dict into matching entries
    in a target fig_dict for all data_series that include a 'simulate' or 'equation' block.
    It supports both parallel updates by index and matching by series name.

    Args:
        target_fig_dict (dict): The figure dictionary to update.
        source_fig_dict (dict): The source figure dictionary providing updated values.
        parallel_structure (bool, optional): If True, updates by index order (zip). If False,
            matches series by their "name" field. Defaults to True.
        modify_target_directly (bool, optional): If True, modifies target_fig_dict in-place.
            If False, operates on a deep copy. Defaults to False.

    Returns:
        dict: The updated target_fig_dict with new x, y, and optionally z values for matched implicit series.
    """
    if modify_target_directly == False:
        import copy  # Import inside function to limit scope   
        updated_fig_dict =  copy.deepcopy(target_fig_dict)  # Deep copy to avoid modifying original
    else:
        updated_fig_dict = target_fig_dict

    target_data_series = updated_fig_dict.get("data", [])
    source_data_series = source_fig_dict.get("data", [])

    if parallel_structure and len(target_data_series) == len(source_data_series):
        # Use zip() when parallel_structure=True and lengths match
        for target_series, source_series in zip(target_data_series, source_data_series):
            if ("equation" in target_series) or ("simulate" in target_series):
                target_series["x"] = list(source_series.get("x", []))  # Extract and apply "x" values
                target_series["y"] = list(source_series.get("y", []))  # Extract and apply "y" values
                if "z" in source_series:
                    target_series["z"] = list(source_series.get("z", []))  # Extract and apply "z" values                    
    else:
        # Match by name when parallel_structure=False or lengths differ
        source_data_dict = {series["name"]: series for series in source_data_series if "name" in series}

        for target_series in target_data_series:
            if ("equation" in target_series) or ("simulate" in target_series):
                target_name = target_series.get("name")
               
                if target_name in source_data_dict:
                    source_series = source_data_dict[target_name]
                    target_series["x"] = list(source_series.get("x", []))  # Extract and apply "x" values
                    target_series["y"] = list(source_series.get("y", []))  # Extract and apply "y" values
                    if "z" in source_series:
                        target_series["z"] = list(source_series.get("z", []))  # Extract and apply "z" values                    
    return updated_fig_dict


def execute_implicit_data_series_operations(fig_dict, simulate_all_series=True, evaluate_all_equations=True, adjust_implicit_data_ranges=True, adjust_offset2d=False, adjust_arrange2dTo3d=False):
    """
    Processes data_series dicts in a fig_dict, executing simulate/equation-based series as needed, including setting the simulate/equation evaluation ranges as needed,
    then provides the simulated/equation-evaluated data into the original fig_dict without altering original fig_dict implicit ranges.

    This function evaluates and simulates any data_series entries in the fig_dict that use "simulate"
    or "equation" blocks. It creates a deep copy of the figure to avoid overwriting original range
    configurations (such as x_range_default). Simulated and evaluated data is extracted from the copy
    and merged back into the original fig_dict for use in rendering.

    Args:
        fig_dict (dict): The main figure dictionary that may contain implicit (simulate/equation) data_series.
        simulate_all_series (bool, optional): Whether to simulate all series requiring it. Defaults to True.
        evaluate_all_equations (bool, optional): Whether to evaluate all equation-based series. Defaults to True.
        adjust_implicit_data_ranges (bool, optional): Whether to adapt x-axis ranges of implicit series 
            using non-implicit data ranges. Defaults to True.

    Returns:
        dict: The updated fig_dict with fresh data inserted into simulated or equation-driven series,
        while preserving their original metadata and x_range_default boundaries.
    """
    import copy  # Import inside function for modularity
    # Create a copy for processing implicit series separately
    fig_dict_for_implicit = copy.deepcopy(fig_dict)
    #first check if any data_series have an equatinon or simulation field. If not, we'll skip.
    #initialize with false:
    implicit_series_present = False

    for data_series in fig_dict["data"]:
        if ("equation" in data_series) or ("simulate" in data_series):
            implicit_series_present = True
    if implicit_series_present == True:
        if adjust_implicit_data_ranges:
            # Retrieve ranges from data series that are not equation-based or simulation-based.
            fig_dict_ranges, data_series_ranges = get_fig_dict_ranges(fig_dict, skip_equations=True, skip_simulations=True)
            data_series_ranges # Variable not used. The remainder of this comment is to avoid vs code pylint flagging. pylint: disable=pointless-statement
            # Apply the extracted ranges to implicit data series before simulation or equation evaluation.
            fig_dict_for_implicit = update_implicit_data_series_x_ranges(fig_dict, fig_dict_ranges)

        if simulate_all_series:
            # Perform simulations for applicable series
            fig_dict_for_implicit = simulate_as_needed_in_fig_dict(fig_dict_for_implicit)
            # Copy data back to fig_dict, ensuring ranges remain unchanged
            fig_dict = update_implicit_data_series_data(target_fig_dict=fig_dict, source_fig_dict=fig_dict_for_implicit, parallel_structure=True, modify_target_directly=True)

        if evaluate_all_equations:
            # Evaluate equations that require computation
            fig_dict_for_implicit = evaluate_equations_as_needed_in_fig_dict(fig_dict_for_implicit)
            # Copy results back without overwriting the ranges
            fig_dict = update_implicit_data_series_data(target_fig_dict=fig_dict, source_fig_dict=fig_dict_for_implicit, parallel_structure=True, modify_target_directly=True)
        
    if adjust_offset2d: #This should occur after simulations and evaluations because it could rely on them.
        #First check if the layout style is that of an offset2d graph.
        layout_style = fig_dict.get("plot_style", {}).get("layout_style", "")
        if "offset2d" in layout_style:
            #This case is different from others -- we will not modify target directly because we are not doing a merge.
            fig_dict = extract_and_implement_offsets(fig_dict_for_implicit, modify_target_directly = False) 
    if adjust_arrange2dTo3d: #This should occur after simulations and evaluations because it could rely on them.
        #First check if the layout style is that of an arrange2dTo3d graph.
        layout_style = fig_dict.get("plot_style", {}).get("layout_style", "")
        if "arrange2dTo3d" in layout_style:
            #This case is different from others -- we will not modify target directly because we are not doing a merge.
            fig_dict = implement_arrange2dTo3d(fig_dict_for_implicit, modify_target_directly = False) 

    return fig_dict


def implement_arrange2dTo3d(fig_dict, modify_target_directly=False):
    import copy
    #TODO: add some logic that enables left, right, and vertical axes variables to be determined
    #TODO: add some logic that enables the axes labels to be moved as needed.
    scratch_fig_dict = copy.deepcopy(fig_dict) #initialize. This fig_dict will be modified with pre-processing, then drawn from.
    modified_fig_dict = copy.deepcopy(fig_dict) #initialize.
    vertical_axis_variable = fig_dict["layout"].get("vertical_axis_variable", {})
    if len(vertical_axis_variable) == 0:#This means one was not provided, in which case we'll make a sequential graph with default, which makes y into the vertical axis.
        vertical_axis_variable = 'y'
    left_axis_variable = fig_dict["layout"].get("left_axis_variable", {})
    if len(left_axis_variable) == 0:#This means one was not provided, in which case we'll make a sequential graph with default, which makes x into left axis.
        left_axis_variable = 'x'
    right_axis_variable = fig_dict["layout"].get("right_axis_variable", {})
    if len(right_axis_variable) == 0:#This means one was not provided, in which case we'll make an ascending sequence for the right-axis, which we initiate as "ascending_sequence"
        right_axis_variable = 'data_series_index_vector'        
        #Now we'll populate the ascending sequence into each data_series.
        for data_series_index in range(len(fig_dict["data"])):
            length_needed = len(fig_dict["data"][data_series_index]["x"])
            data_series_index_vector = [data_series_index] * length_needed #this repeats the data_series_index as many times as needed in a list.
            scratch_fig_dict["data"][data_series_index]["data_series_index_vector"] = data_series_index_vector
    #Now, need to rearrange the axes labels as needed.
    # Ensure nested structure for xaxis, yaxis, and zaxis titles exists
    #For plotly 3D axes: y is left, x is right, and z is up.
    for axis in ["xaxis", "yaxis", "zaxis"]:
        modified_fig_dict.setdefault("layout", {}).setdefault(axis, {}).setdefault("title", {})["text"] = ""
    modified_fig_dict["layout"]["yaxis"]["title"]["text"] = scratch_fig_dict["layout"][str(left_axis_variable)+"axis"]["title"]["text"] 
    if right_axis_variable != "data_series_index_vector":
        modified_fig_dict["layout"]["xaxis"]["title"]["text"] = scratch_fig_dict["layout"][str(right_axis_variable)+"axis"]["title"]["text"]  
    else: #This means it's sequence of data series.
        modified_fig_dict["layout"]["xaxis"]["title"]["text"] = "Data Set"
    modified_fig_dict["layout"]["zaxis"]["title"]["text"] = scratch_fig_dict["layout"][str(vertical_axis_variable)+"axis"]["title"]["text"]  
    #Now, need to rearrange the variables as would be expected, and need to do it for each data series.
    for data_series_index in range(len(fig_dict["data"])):
        #We will support two trace_styles: scatter3d and curve3d.
        if "scatter" in modified_fig_dict["data"][data_series_index]["trace_style"]:
            modified_fig_dict["data"][data_series_index]["trace_style"] = "scatter3d" #This is currently the only supported trace style. Need to add some logic.
        else:
            modified_fig_dict["data"][data_series_index]["trace_style"] = "curve3d" #This is currently the only supported trace style. Need to add some logic.
        #For plotly 3D axes: y is left, x is right, and z is up.
        modified_fig_dict["data"][data_series_index]["y"] = scratch_fig_dict["data"][data_series_index][left_axis_variable]
        modified_fig_dict["data"][data_series_index]["x"] = scratch_fig_dict["data"][data_series_index][right_axis_variable]
        modified_fig_dict["data"][data_series_index]["z"] = scratch_fig_dict["data"][data_series_index][vertical_axis_variable]
    return modified_fig_dict


#Small helper function to find if an offset is a float scalar.
def is_float_scalar(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False

def extract_and_implement_offsets(fig_dict, modify_target_directly=False, graphical_dimensionality=2):
    import numpy as np
    #First, extract offsets.
    import copy
    if modify_target_directly == False:
        fig_dict_with_offsets = copy.deepcopy(fig_dict)
    else:
        fig_dict_with_offsets = fig_dict
    #initialize offset_variable_name as the case someone decides to specify one.
    offset_variable_name = ""
    if "offset" in fig_dict["layout"]:
        #This is the easy case, because we don't need to determine the offset.
        offset = fig_dict["layout"]["offset"]
        if is_float_scalar(offset):
            offset = fig_dict["layout"]["offset"]
        elif isinstance(offset,str):#check if is a string, in which case it is a variable name.
            #in this case it is a variable where we will extract it from each dataset.
            offset_variable_name = offset
        else:   
            #Else assume the offset is an array like object, of length equal to number of datapoints.
            offset = np.array(offset, dtype=float)
        #Now, implement offsets.
        if graphical_dimensionality == 2:
            current_series_offset = 0  # Initialize total offset
            for data_series_index in range(len(fig_dict["data"])):
                data_series_y_values = np.array(fig_dict["data"][data_series_index]["y"])
                if data_series_index == 0:
                    fig_dict_with_offsets["data"][data_series_index]["y"] = list(data_series_y_values)
                else:
                    # Determine the current offset
                    if offset_variable_name != "":
                        incremental_offset = np.array(fig_dict["data"][data_series_index][offset_variable_name], dtype=float)
                    else:
                        incremental_offset = np.array(offset, dtype=float)
                    current_series_offset += incremental_offset  # Accumulate the offset
                    fig_dict_with_offsets["data"][data_series_index]["y"] = list(data_series_y_values + current_series_offset)
    else:
        #This is the hard case, we need to determine a reasonable offset for the dataseries.
        if graphical_dimensionality == 2:
            fig_dict_with_offsets = determine_and_apply_offset2d_for_fig_dict(fig_dict, modify_target_directly=modify_target_directly)
    return fig_dict_with_offsets

    #A function that calls helper functions to determine and apply a 2D offset to fig_dict
def determine_and_apply_offset2d_for_fig_dict(fig_dict, modify_target_directly=False):
    if modify_target_directly == False:
        import copy
        fig_dict = copy.deepcopy(fig_dict)
    #First, extract data into a numpy array like [[x1, y1], [x2, y2], ...]
    all_series_array = extract_all_xy_series_data_from_fig_dict(fig_dict)
    #Then determine and apply a vertical offset. For now, we'll only support using the default
    #argument which is 1.2 times the maximum height in the series.
    #If someone wants to do something different, they can provide their own vertical offset value.
    offset_data_array = apply_vertical_offset2d_for_numpy_arrays_list(all_series_array)
    #Then, put the data back in.
    fig_dict = inject_xy_series_data_into_fig_dict(fig_dict=fig_dict, data_list = offset_data_array)
    return fig_dict

def extract_all_xy_series_data_from_fig_dict(fig_dict):
    """
    Extracts all x and y values from a Plotly figure dictionary into a list of NumPy arrays.
    Each array in the list has shape (n_points, 2), where each row is [x, y] like [[x1, y1], [x2, y2], ...].
    """
    import numpy as np
    series_list = []
    for data_series in fig_dict.get('data', []):
        x_vals = np.array(data_series.get('x', []))
        y_vals = np.array(data_series.get('y', []))
        #Only keep the xy data if x and y lists are the same length.
        if len(x_vals) == len(y_vals):
            series_list.append(np.stack((x_vals, y_vals), axis=-1))
    return series_list

def apply_vertical_offset2d_for_numpy_arrays_list(data_list, offset_multiplier=1.2):
    """
    Applies vertical offsets to a list of 2D NumPy arrays.
    Each array has shape (n_points, 2), with rows like [[x1, y1], [x2, y2], ...].
    Returns a list of the same structure with adjusted y values per series index.
    """
    import numpy as np
    spans = [np.max(series[:, 1]) - np.min(series[:, 1]) if len(series) > 0 else 0 for series in data_list]
    base_offset = max(spans) * offset_multiplier if spans else 0
    offset_data_list = []
    for series_index, series_array in enumerate(data_list):
        # Skip empty series but preserve its position in the output
        if len(series_array) == 0:
            offset_data_list.append(series_array)
            continue
        # Ensure float type for numerical stability when applying offsets
        offset_series = np.copy(series_array).astype(float)
        # Apply vertical offset based on series index and base offset
        #print("line 5574, before the addition", offset_series)
        offset_series[:, 1] += series_index * base_offset
        #print("line 5576, after the addition", offset_series)
        # Add the adjusted series to the output list
        offset_data_list.append(offset_series)
    return offset_data_list




def inject_xy_series_data_into_fig_dict(fig_dict, data_list):
    """
    Updates a Plotly figure dictionary in-place by injecting x and y data from a list of NumPy arrays.
    Each array must have shape (n_points, 2), where each row is [x, y] like [[x1, y1], [x2, y2], ...].
    The number of arrays must match the number of traces in the figure.
    """
    n_traces = len(fig_dict.get('data', []))
    if len(data_list) != n_traces:
        raise ValueError("Mismatch between number of traces and number of data series.")
    for i, trace in enumerate(fig_dict['data']):
        series = data_list[i]
        trace['x'] = series[:, 0].tolist()
        trace['y'] = series[:, 1].tolist()
    return fig_dict

### End of section of file that has functions for "simulate" and "equation" fields, to evaluate equations and call external javascript simulators, as well as support functions###

# Example Usage
if __name__ == "__main__":
    # Example of creating a record with optional attributes.
    Record = JSONGrapherRecord(
        comments="Here is a description.",
        graph_title="Here Is The Graph Title Spot",
        data_objects_list=[
            {"comments": "Initial data series.", "uid": "123", "name": "Series A", "trace_style": "spline", "x": [1, 2, 3], "y": [4, 5, 8]}
        ],
    )
    x_label_including_units= "Time (years)" 
    y_label_including_units = "Height (m)"
    Record.set_comments("Tree Growth Data collected from the US National Arboretum")
    Record.set_datatype("Tree_Growth_Curve")
    Record.set_x_axis_label_including_units(x_label_including_units)
    Record.set_y_axis_label_including_units(y_label_including_units)


    Record.export_to_json_file("test.json")

    print(Record)

    # Example of creating a record from an existing dictionary.
    example_existing_JSONGrapher_record = {
        "comments": "Existing record description.",
        "graph_title": "Existing Graph",
        "data": [
            {"comments": "Data series 1", "uid": "123", "name": "Series A", "type": "spline", "x": [1, 2, 3], "y": [4, 5, 8]}
        ],
    }
    Record_from_existing = JSONGrapherRecord(existing_JSONGrapher_record=example_existing_JSONGrapher_record)
    x_label_including_units= "Time (years)" 
    y_label_including_units = "Height (cm)"
    Record_from_existing.set_comments("Tree Growth Data collected from the US National Arboretum")
    Record_from_existing.set_datatype("Tree_Growth_Curve")
    Record_from_existing.set_x_axis_label_including_units(x_label_including_units)
    Record_from_existing.set_y_axis_label_including_units(y_label_including_units)
    print(Record_from_existing)
    
    print("NOW WILL MERGE THE RECORDS, AND USE THE SECOND ONE TWICE (AS A JSONGrapher OBJECT THEN JUST THE FIG_DICT)")
    print(merge_JSONGrapherRecords([Record, Record_from_existing, Record_from_existing.fig_dict]))



