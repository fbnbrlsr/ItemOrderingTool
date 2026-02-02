import eel
from algorithm import optimal_parts_groups

# Initialize eel with the web folder
eel.init("web")

@eel.expose
def compute_groups(user_input, max_length):
    
    # Debug
    print(" --- Received --- ")
    print("Input type:", type(user_input))
    print("Input:", user_input)
    print("max_length:", max_length)
    
    # Pre-process
    try:
        flat_list = [float(x) for row in user_input for x in row]
        max_length = float(max_length)
    except:
        print("ERROR while parsing input")
    
    # Compute groups
    groups_dict = optimal_parts_groups(flat_list, max_length)
    
    
    # Post-process
    result_list = []
    for k in groups_dict:
        print(f"Group {k}: {groups_dict[k]} -> sum: {sum(groups_dict[k])}")
        result_list.append(sorted(groups_dict[k][::-1]))

    result_list = sorted(result_list, key=lambda x: sum(x))[::-1]
    print("result_list:", result_list)
    
    return result_list
    
    


# Start the application
eel.start("index.html", size=(1300, 800))
