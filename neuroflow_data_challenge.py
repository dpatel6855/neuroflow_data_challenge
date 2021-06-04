import pandas as pd
import matplotlib.pyplot as plt
##################################
#
#For correct plot visualization please run the following command on the python console:
#   %matplotlib qt
#Or just set matplotlib plots to plot in external windows
#################################
GAD7_df = pd.read_csv('phq_all_final.csv') #Reading the CSV file into a datafram
score_threshold = 10 #Threshold for anxiety disorders
patient_ids = list(GAD7_df['patient_id'].unique()) #list of patients id from the CSV file
GAD7_df = GAD7_df.sort_values(by='date') #sort the database by date, from oldest to newest
patients_info = {} #Dictionary where all the information from each patient will be stored
max_number_of_sessions = 0 #Max number of sessions a patient gets
def fill_patients_info_data(session): #Function to fill the patients_info dictionary from the dataframe
    if session['patient_id'] not in patients_info.keys(): #If it's the first time the patient id appears in the dataframe we initialize his data
        session_info = {'date_created':session['patient_date_created'],
                        'first_session_date':session['date'],
                        'session_1_score':session['score'],
                        'number_of_sessions':1} #Number of sessions the patient has assisted
        patients_info[session['patient_id']] = session_info  #Save the initial information from the patient
    else: #If it's not the first time the patient appears in the database, means it's not his first session
        patients_info[session['patient_id']]['number_of_sessions'] += 1 #Increase the number of sessions of the patient by 1
        session_number = patients_info[session['patient_id']]['number_of_sessions']
        patients_info[session['patient_id']]['session_'+str(session_number) + '_score'] = session['score'] #Store the score of the session in a new key representing the current session
        patients_info[session['patient_id']]['improvement'] = session['score'] - patients_info[session['patient_id']]['session_1_score'] #Calculate the improvement of the patient, which means the difference in the score of the last session and the first one
        global max_number_of_sessions
        if session_number > max_number_of_sessions: #Change the maximum number of sessions if the current patient's number of sessions is higher
            max_number_of_sessions = session_number

GAD7_df.apply(fill_patients_info_data, axis=1) #Apply the function to all rows of the GAD7 dataframe to fill the patients_info dictionary

patients_info_df = pd.DataFrame.from_dict(patients_info, orient='index')  #Create a dataframe from the dict filled before
sessions_names = ['session_'+str(num)+'_score' for num in range(1,max_number_of_sessions+1)] #Build a list of the session names for plotting purposes

improvement_info = {} #Dictionary to store the improvement data in order to plot it vs number of sessions
for number_of_sessions in range(2,max_number_of_sessions+1): #Iterate through each possible value of number of sessions
    number_of_patients = len(patients_info_df[patients_info_df['number_of_sessions']==number_of_sessions]['improvement']) #Get the patients that have the given number of sessions
    if number_of_patients>0: #If there's more than one patient
        mean = patients_info_df[patients_info_df['number_of_sessions']==number_of_sessions]['improvement'].mean() #Get the mean improvement of each number of sessions
        improvement_info[number_of_sessions] = {}
        improvement_info[number_of_sessions]['mean'] = mean #Save the mean to the dictionary with the key as the number of sessions
        improvement_info[number_of_sessions]['number_of_patients'] = number_of_patients
improvement_info_df = pd.DataFrame.from_dict(improvement_info,orient='index')   #Create a dataframe from the dict filled before

#Plotting patients score per session number
plt.figure()
patients_info_df.boxplot(column=sessions_names)
positions = tuple(range(1,max_number_of_sessions))
labels = tuple(range(1,max_number_of_sessions))
plt.xticks(positions, labels,rotation=90)
plt.show()
plt.title('Patients score per session number')
plt.xlabel('Session')
plt.ylabel('Score')

#Plotting improvement and number of patients in terms of number of sessions
fig2 = plt.figure(figsize=[8,8]) # Create matplotlib figure
ax = fig2.add_subplot(111) # Create matplotlib axes
ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.
width = 0.4
bar1 = improvement_info_df['number_of_patients'].plot(kind='bar', color='blue', ax=ax, width=width, position=0,label='Patients')
bar2 = improvement_info_df['mean'].plot(kind='bar', color='red', ax=ax2, width=width, position=1,label='Mean')

lines_1, labels_1 = ax.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()

lines = lines_1 + lines_2
labels = labels_1 + labels_2

ax.legend(lines, labels, loc=0)


ax.set_ylabel('Number of patients')
ax2.set_ylabel('Improvement')
plt.title('Improvement and number of patients in terms of number of sessions')
plt.show()

#Example plotting of a specific patient progress
patient_id = 5251
patient_info = patients_info_df.loc[patient_id]
columns_names = ['session_'+str(num)+'_score' for num in range(1,patient_info['number_of_sessions']+1)]
patient_scores = list(patient_info[columns_names])
plt.figure()
plt.bar(list(range(1,patient_info['number_of_sessions']+1)),patient_scores)
plt.title('Patient progress')
plt.xlabel('Session')
plt.ylabel('GDA7 score')
plt.show()

insigths = """
There are a series of insights we can get from doing a brief but effective data analysis on the database provided, at first,
on the "patient score per session number" chart, we can appreciate that all the patients except for one had assisted to 42
or fewer sessions. During the first 6 sessions, we can see a good improvement from the group in general, lowering the scores
obtained in the GAD7 test, but from there it starts to oscillate and increase the group score, this can mean that the people
that had to assist to this many sessions do not present improvement or that they get even worst, this is an important insight,
as we would expect the patients to get better as time passes and they get tested.

There's something quite strange from the data, there's one patient that has an oscillating behavior across all sessions, 
this may translate to a corrupted data or to a very special case.

From the "Improvement and number of patients in terms of number of sessions" graph, there's a very interesting analysis to 
be made. From the patients' side, we see a reasonable behavior, it decreases kind of exponentially as the number of sessions 
decrease, nothing strange about it, and so does the average improvement of these patients, with a bit of oscillation, but, 
from around the 13 sessions (this is: patients who had in total 13 or more sessions), this oscillation increases dramatically, 
we can even see there are some patients, that took the test a quite big amount of times, and yet presented worst results than 
their first time, there's something really special about these data points, either something's happening with these patients 
that are making them to get worst in their condition or the data points are not valid.

Regarding the problem of not being able to visualize correctly the progress of the patients, the patients_info_df 
Dataframe builds from the CSV data and represent each patient as a row, with all their scores organized from each 
session (this is: each time they have taken the test), so this provides a way to correctly visualize each patient 
progress through a bar chart. Doing this and analyzing the data on a regular basis, will allow the therapist to know 
what techniques and treatments do work and which ones do not.
"""
print('Insights from the analyzed data: ')
print(insigths)
