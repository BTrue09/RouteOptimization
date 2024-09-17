#Brayden Truex

#Will be completing the code for my route optimization project for pepsi. 
#Goals for the final output: Calculated Endtime
#                            Optimized Truck Order
#                            Split teams

#Need to gather the information from the converted excel spreadsheets

#Global variable file names
pickerNamesFile = "needed_Files\loader_Names.txt"
performanceFile = "needed_Files\weekly numbers 6-9.txt"
truckNumbersFile = "needed_Files\Truex 6-25.txt"

def get_loader_numbers():
    #need to get a list of the loaders working that day
    #need to get performance stats for either the previous week or the previous day to use
    # and will use the list of workers for that day to grab the ones we need

    with open(pickerNamesFile, 'r') as name_file:
        name_data = name_file.read().splitlines()
    #now all the names in the list name_data
    #need to get the lines in the picker performance file that correspond with each name
    #as well as the index for each of the categories
    #first we will have to read in the file and find the correct categories line
    workers_list = []
    categories = []
    with open(performanceFile, 'r') as performance_file:
        line = performance_file.readline().split('\t')
        #this will read the line and split it into a list that contains all the words
        #we can then check which one is the categories line by knowing how it begins and
        #we can know if it is a needed worker's line by comparing it with the list of workers
        while line and line[0] != 'WAREHOUSE':
            if line[0] == 'User':
                categories = line
            if line[0] in name_data:
                workers_list.append(line)

            line = performance_file.readline().split('\t')
    return categories, workers_list


def get_truck_numbers():
    #will need to reed from a file and store the categories of the trucks and the truck themself
    #there are certain headers/categories we want to get rid of that will affect the index
    #need to get rid of activation time and door. 
    
    #open the file and begin working
    categories = []
    routes_list = []
    with open(truckNumbersFile, 'r') as truck_file:
        line = truck_file.readline().split('\t')
        #reads the first line of the file and splits it into a list by the tab character
        #the first line in the truck file is the categories so just need to get rid of 
        #the specific categories listed above so when the rest of the file is read in it
        #will be complete
        #remove_headers = {'Activation Time', 'Door'}
        #categories = [x for x in line if x not in remove_headers]
        categories = line

        #reading in all of the lines in the truck file
        for line in truck_file:
            line = line.split('\t')
            routes_list.append(line)
    return categories, routes_list


def find_Category(category_Name, categories):
    for i, v in enumerate(categories):
        if v== category_Name:
            return i



def convert_Time_To_Min(current_Time_Index, routes_list):
    for i, route in enumerate(routes_list):
        current_Time = route[current_Time_Index]
        #starts as '00:00:00
        target_Index = current_Time.find(':')
        hour = int(current_Time[1:target_Index])
        #changes to 00:00
        current_Time = current_Time[target_Index + 1:]
        target_Index = current_Time.find(':')
        minute = int(current_Time[:target_Index])
        #should have num hrs in hour, and minutes in minute
        total_Time = hour*60 + minute
        routes_list[i][current_Time_Index] = total_Time

def alter_Time(half_Pallets_Index, total_Pallets_Index, current_Time_Index, routes_list):
    #will change the time for each of the routes individually and will see a change in the sum
    #by the end of it. 
    #To start the avg half pallet time that we will use is 12 minutes
    for i, route in enumerate(routes_list):
        #need num half and full pallets for each truck, as well as current time
        num_half_pallets = int(route[half_Pallets_Index])
        num_pallets = int(route[total_Pallets_Index])
        current_Time = int(route[current_Time_Index])

        #have the data that we need, now just need to calculate the data
        if num_half_pallets and num_pallets:
            # Calculate the time contribution from full pallets
            num_full_pallets = abs(num_pallets-num_half_pallets)
            full_pallet_time = (current_Time / num_pallets) * num_full_pallets
            # Calculate the time contribution from half pallets
            half_pallet_time = int(num_half_pallets / 2) * 17
            # Total time is the sum of the contributions
            total_time = full_pallet_time + half_pallet_time
            # Update the current time in the routes_list
            routes_list[i][current_Time_Index] = int(total_time)

        

def calculate_Truck_Time(truck_categories, routes_list):
    #need to find the index, this will be done frequently throughout the code and the indices are
    #based on the categories lists so can create a function do this effortlessly
    #to calculate the truck time will need multiple pieces:
    #   Trucks current estimated time
    #   Total num half pallets
    #   Avg half pallet time **This will be a value that will be created and made up**
    #   Total num pallets
    current_Time_Index = find_Category('Planned Pallet Time', truck_categories)
    half_Pallets_Index = find_Category('Total # of Half Pallet', truck_categories)
    total_Pallets_Index = find_Category('Pick Pal.', truck_categories)

    #now that we have the indices needed for calculating the new truck times can calculate
    #new estimated route times. Can pass the current_Time to a function that will calculate
    #time in minutes. Then when we need to print the times at the end can convert to hrs, min
    convert_Time_To_Min(current_Time_Index, routes_list)

    #Now all times are in minutes so now we need to account for workers doing half pallets
    #and being able to do 2 at a time so that changes the amnt of time by a little bit
    #so we should acct for that
    alter_Time(half_Pallets_Index, total_Pallets_Index, current_Time_Index, routes_list)
    #all routes should be in minutes and should be adjusted to incorporate 2 half pallets
    #being completed at a time
    
def sort_Trucks(truck_categories, routes_list):
    #will be sorting the trucks by the estimated time index
    estimated_time_index = find_Category('Planned Pallet Time', truck_categories)
    pick_Cases_Index = find_Category('Pick Cases', truck_categories)
    #this sorts the lists based on their times
    #routes_list.sort(key=lambda x: x[estimated_time_index], reverse=True)
    #need to try and sort the trucks based on a ratio of their cases to time
    routes_and_ratios = []
    for route in routes_list:
        if route[estimated_time_index] != 0:
            cpm = int(route[pick_Cases_Index]) / int(route[estimated_time_index])
            routes_and_ratios.append((route, cpm))
    
    routes_and_ratios.sort(key=lambda x:x[1], reverse=True)
    routes_list.sort(key=lambda x:x[estimated_time_index], reverse=True)

    truck_team1 = routes_and_ratios[:5]
    truck_team1_routes = [route[0] for route, _ in truck_team1]

    truck_team2 = routes_and_ratios[5:-5]
    truck_team2_routes = [route[0] for route, _ in truck_team2]

    truck_team3 = routes_and_ratios[-5:]
    truck_team3_routes = [route[0] for route, _ in truck_team3]

    return truck_team1_routes, truck_team2_routes, truck_team3_routes

    


def sort_Workers(worker_categories, workers_list):
    #for the workers will sort the workers_list based on pick efficiency
    worker_Pick_Index = find_Category('Pick Efficiency', worker_categories)
    for i, worker in enumerate(workers_list):
        percentage = worker[worker_Pick_Index]
        target_Index = int(percentage.find('%'))
        worker[worker_Pick_Index] = int(percentage[0:target_Index])
    workers_list.sort(key=lambda x: x[worker_Pick_Index])
    #now that everything is sorted will be easily able to create teams

def create_Teams(worker_categories, workers_list):
    #so for this we need to map the route with what team it will be scheduled for
    #will have team 1 be the best pickers and team 3 be the slowest or worst
    #team 3 for the workers will be a hard cutoff and the those below 65 percent
    team1 = []
    team2 = []
    team3 = []
    worker_Pick_Index = find_Category('Pick Efficiency', worker_categories)
    worker_Name = find_Category('User', worker_categories)
    for i, worker in enumerate(workers_list):
        name = worker[worker_Name]
        if int(worker[worker_Pick_Index]) <= 65:
            team3.append(name)
        else:
            #finding the rest of the teams won't be as easy to do
            #preferably will just split them in half or only take the top 2-3 workers
            #for team 1
            #lets start with taking the top 3 and go from there
            num_Workers = len(workers_list)
            if i < num_Workers - 2:
                team2.append(name)
            else:
                team1.append(name)
    
    return team1, team2, team3

def optimize_Route_File_Trucks(truck_categories, routes_list, team1, team2, team3):
    #to do this will split this up into 2 sections
    #the first will be for truck routes and the second will be for the workers
    #Trucks:
    #Need to first get all of the needed categories and variables
    route_Index = find_Category('Local Route', truck_categories)
    pick_Cases_Index = find_Category('Pick Cases', truck_categories)
    chill_Pallets_Index = find_Category('Chill Pal.', truck_categories)
    full_Pallets_Index = find_Category('Full Pal.', truck_categories)
    pick_Pallets_Index = find_Category('Pick Pal.', truck_categories)
    pick_Time_Index = find_Category('Planned Pallet Time', truck_categories)
    #Now that we have each of the different categories will just need to print for each route
    #first print the headers
    num_Routes = len(routes_list)
    print('Local Route\tPick Cases\tChill Pal.\tFull Pal.\tPick Pal.\tTeam\t\tPick Time\n')
    #now will need to print out each of the routes
    for i, route in enumerate(routes_list):
        route_Num = route[route_Index]
        pick_Cases = route[pick_Cases_Index]
        chill_Pallets = route[chill_Pallets_Index]
        full_Pallets = route[full_Pallets_Index]
        pick_Pallets = route[pick_Pallets_Index]
        pick_Time = route[pick_Time_Index]
        #Now have to figure out the team

        if route_Num in team1:
            team = 'Team 1'
        elif route_Num in team2:
            team = 'Team 2'
        else:
            team = 'Team 3'
        #HAVE TO CONVERT TIME BACK TO HOURS AND NUMBERS 
        hours = int(pick_Time / 60)
        minutes = pick_Time % 60
        if minutes < 10:
            print(route_Num,'\t\t',pick_Cases,'\t\t',chill_Pallets,'\t\t',full_Pallets,'\t\t',pick_Pallets,'\t\t',team,'\t\t',hours,':0',minutes)
        else:
            print(route_Num,'\t\t',pick_Cases,'\t\t',chill_Pallets,'\t\t',full_Pallets,'\t\t',pick_Pallets,'\t\t',team,'\t\t',hours,':',minutes)
        
def add_Team(team1, team2, team3):
    #in this file we will display the teams and who is on what team
    print('Team 1: ', team1)
    print('Team 2: ', team2)
    if(len(team3) > 0):
        print('Team 3: ', team3)

def add_Total_Time(truck_categories, routes_list, workers_list, worker_categories):
    time_Index = find_Category('Planned Pallet Time', truck_categories)
    sum = 0
    for i, route in enumerate(routes_list):
        sum = sum + route[time_Index]
    
    performance_Category = find_Category('Pick Efficiency', worker_categories)
    sum_Percentage = 0
    num_workers = len(workers_list)
    for i, worker in enumerate(workers_list):

        stat_To_Add = int(worker[performance_Category])
        if stat_To_Add >= 65:
            sum_Percentage = sum_Percentage + stat_To_Add
        else:
            num_workers = num_workers - 1

    sum_Percentage = sum_Percentage / 100
    total_Time = int(sum / sum_Percentage)

    hours = int(total_Time/60)
    minutes = total_Time % 60
    if int(minutes) < 10:
        print('Estimated Total Time: ', hours, ':0', minutes)
    else:
        print('Estimated Total Time: ', hours, ':', minutes)


def main():
    
    #when all files are in need to start using those files
    # start with getting the workers info and go from there
    worker_categories, workers_list = get_loader_numbers()

    #have the information needed for the pickers, now need to get the truck info
    truck_categories, routes_list = get_truck_numbers()
        
    #now have loaded all of the data from the files into the program to be used
    #have to determine the best course of action for using this data
    #need to determine how we are going to set up the sharable file
    #need to determine how we are going to order the trucks
    #will follow a 2-2-1 approach to begin and will explore
    #need to determine how we are going to estimate the ending time for the shift
    calculate_Truck_Time(truck_categories, routes_list)

    #after the trucks times have been adjusted we should sort the trucks
    #then we need to determine what truck gets assigned to what team
    truck_Team1, truck_Team2, truck_Team3 = sort_Trucks(truck_categories, routes_list)

    #can do the truck teams at the end, the bigger priority is spliting the workers up
    #and then at the end splitting the trucks amongst those workers. 
    sort_Workers(worker_categories, workers_list)
    team1, team2, team3 = create_Teams(worker_categories, workers_list)
        
    #now we have our teams and routes in order
    #the biggest x 1/4 of the trucks will be for team 1
    #the majority will be for team 2
    #and then the final quarter will be for team 3
    optimize_Route_File_Trucks(truck_categories, routes_list, truck_Team1, truck_Team2, truck_Team3)
    add_Team(team1, team2, team3)
    add_Total_Time(truck_categories, routes_list, workers_list, worker_categories)


if __name__ == "__main__":
    main()

