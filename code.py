def load_driving_times(filepath):
    with open(filepath, 'r') as file:
        # Creates a 2D list where driving_times[from_node][to_node] gives the time in seconds
        return [[int(time) for time in line.strip().split('\t')] for line in file]

def load_orders(filepath):
    orders = {}
    with open(filepath, 'r') as file:
        # Skip the header row
        next(file) 
        
        for line in file:
            parts = line.strip().split('\t')
            
            # Skip empty lines just in case
            if len(parts) < 27: 
                continue 
                
            order_id = int(parts[0])
            orders[order_id] = {
                'node_id': int(parts[2]),       
                'duration': int(parts[5]),      
                'profit': float(parts[6]),      
                'eligibility': [int(x) for x in parts[7:27]] 
            }
    return orders

def generate_initial_solution(orders, driving_times):
    num_students = 20
    hq_node = 251 # Headquarters [cite: 23]
    max_shift_seconds = 8 * 60 * 60 # 8 hours in seconds 

    # Initialize empty schedules for each student
    # schedule[student_id] will hold a list of order IDs
    schedule = [[] for _ in range(num_students)]
    
    # Keep track of which orders haven't been done yet
    unassigned_orders = list(orders.keys())
    
    for student_id in range(num_students):
        current_node = hq_node
        current_time = 0 # Track shift time in seconds
        
        # We iterate over a copy [:] so we can safely remove items from the original list
        for order_id in unassigned_orders[:]:
            order = orders[order_id]
            
            # Constraint 1: Can this student handle this order? [cite: 25, 26, 27]
            if order['eligibility'][student_id] == 1:
                order_node = order['node_id']
                # Convert duration from minutes to seconds for easier math [cite: 19]
                duration_sec = order['duration'] * 60 
                
                # Calculate drive times [cite: 22]
                drive_to_order = driving_times[current_node][order_node]
                drive_to_hq_after = driving_times[order_node][hq_node]
                
                # Constraint 2 & 3: Does it fit in the 8-hour shift, including the drive home? 
                if current_time + drive_to_order + duration_sec + drive_to_hq_after <= max_shift_seconds:
                    
                    # Assign the order!
                    schedule[student_id].append(order_id)
                    
                    # Update student's clock and location
                    current_time += drive_to_order + duration_sec
                    current_node = order_node
                    
                    # Remove from the unassigned pool
                    unassigned_orders.remove(order_id)
                    
    return schedule

if __name__ == "__main__":
    print("Loading data...")
    driving_times = load_driving_times('drivingtimes.txt')
    orders = load_orders('orders.txt')
    
    print("Generating initial schedule...")
    initial_schedule = generate_initial_solution(orders, driving_times)
    
    # Let's see how many orders our naive algorithm managed to assign
    total_assigned = sum(len(route) for route in initial_schedule)
    print(f"Successfully assigned {total_assigned} out of {len(orders)} orders!")
