# This is for tabular data manipulation
import pandas as pd
import numpy as np

# This is for drawing graphs
import plotly.express as px
import plotly.graph_objects as go

# This is for streamlit to deploy app
import streamlit as st

# This is for sql
import mysql.connector

# datetime
import datetime as datetime

# Some CONSTANT
DEFAULT_START_TIME = datetime.date(2022, 11,28)
DEFAULT_END_TIME = datetime.date(2022,12,1)


# Connect to database
db = mysql.connector.connect(
    host = st.secrets['HOST'],
    port = 3306,
    user= st.secrets['USER'],
    passwd = st.secrets['PASSWORD'],
    database = st.secrets['DATABASE']

)

my_cursor = db.cursor()


# Will return dataframe from SQL query
def QueryToDataframe(query, columns_to_convert = []):

    # In case you want to put any extra variable to query
    st.code(query)
    my_cursor.execute(query)

    # Get the data and 
    data = my_cursor.fetchall()
    columns = my_cursor.column_names

    df = pd.DataFrame(data, columns= columns)

    # convert form timedelta to datetime64
    if columns_to_convert != []:
        for column in columns_to_convert:
            df[column] = df[column].values.astype('datetime64[ns]')
            df[column] = df[column].dt.time
    
    return df

def PrintDataframeStreamlit(df):
    df_copy = df.copy()
    for column in df_copy.columns:
        df_copy[column] = df_copy[column].astype(str)

    st.dataframe(df_copy)
    return df

def Graph_1():
    st.markdown('## 1. The availability of rooms throughout the day ')
    st.write('##### The graph below shows the availability of rooms at USF at different hours in one day')

    # Select the day to view
    date = st.date_input(
        'Select the date you want to view',
        DEFAULT_START_TIME,
        min_value=DEFAULT_START_TIME
    )
    st.write("you selected day: " , date)


    # Select the rooms you want to view
    floors = st.multiselect(
        label= "Select the floor you want to view",
        options=["second floor", "third floor", "fourth floor", "fifth floor"],
        default= ["fifth floor"]
    )

    rooms_to_show = []

    for floor in floors:
        if floor == "second floor":
            rooms_to_show.extend(['257', '258'])
        elif floor == "third floor":
            rooms_to_show.extend(['305', '306', '356', '357', '358'])
        elif floor == "fourth floor":
            rooms_to_show.extend(['436', '437','438', '440', '441', '442']) 
        elif floor == "fifth floor":
            rooms_to_show.extend(['514A', '514B', '514C', '514D', '520A','520B', '520C', '520D'])

    

    # Get data from SQL query
    query = '''
    SELECT	
        HOUR(checking_time) AS checking_hour,
		room, 
        COUNT(status) AS total_cnt,
        SUM(CASE
            WHEN status = 'Available' THEN 1
            ELSE 0
            END) AS available_cnt,
		(SUM(CASE
            WHEN status = 'Available' THEN 1
            ELSE 0
            END)/ COUNT(status) ) * 100 AS available_percent
    FROM library_schedule 
    WHERE checking_date = {date} AND room IN {rooms}
    GROUP BY room, checking_hour
    ORDER by room
    '''.format(date = "'{date}'".format(date = date)  , rooms = tuple(rooms_to_show))

    # Now get the df from query and print it out
    df = QueryToDataframe(query=query )
    PrintDataframeStreamlit(df = df)

    st.write(''' **Graph interaction**
    1. You can interact with the graph by clicking on each lines in the legend on the right  
    2. **Double** click on the line in the legend to seperate it
    ''')


    # Now draw the graph
    plot = px.line( data_frame=df, x = "checking_hour", y = "available_percent", 
                color = "room", 
                symbol='room',
                title= "The percentage of availability of each room throughout the day")
    st.plotly_chart(plot, use_container_width=True)

    st.write("#### Graph explanation:")
    st.markdown('''The graph is based on the checking_hour(x axis) and available_percentage(y axis). 
    Basically, I looked at the checking_hour of each room, and calculate the available percentage at that checking hour.      
    For example, I look at checking_hour at 6 of room 257 and have the available percentage of 60%, that means at 6am, 60 percent
    of room 257 is empty, this number can go up or down throught out the day (since I compare the available percentage to the unavailable at
    that moment)
     ''')

def Graph_2():
    st.markdown('## 2. The availability of rooms in different hours ')
    st.write('##### The graph below shows the availability of rooms at different hours in the duration of your choice')

    # Select the start and end date of the view window
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            label= "Select the start day of the duration",
            value= DEFAULT_START_TIME,
            min_value= DEFAULT_START_TIME
        )

    with col2:
        end_date = st.date_input(
            label= "Select the end day of the duration",
            value= DEFAULT_END_TIME,
            min_value= DEFAULT_START_TIME
        )

    query = '''
    SELECT	
        checking_date,
		HOUR(checking_time) AS checking_hour,
        room,
        COUNT(status) AS total_cnt,
        SUM(CASE
            WHEN status = 'Available' THEN 1
            ELSE 0
            END) AS available_cnt,
		(SUM(CASE
            WHEN status = 'Available' THEN 1
            ELSE 0
            END)/ COUNT(status) ) * 100 AS available_percent

    FROM library_schedule
    WHERE checking_date BETWEEN "{start_date}" AND "{end_date}"
    GROUP BY checking_date, checking_hour,room
    ORDER by room
    ;

    
    '''.format(start_date = str(start_date), end_date = str(end_date))

    # Now get the df from query and print it out
    df = QueryToDataframe(query=query )
    PrintDataframeStreamlit(df = df)

    plot = px.line( data_frame=df, x = "checking_date", y = "available_percent", 
                color = "checking_hour", 
                symbol='checking_hour',
                animation_group='checking_hour',
                animation_frame='room',
                title= "The availability at different hours")


    st.plotly_chart(plot)
    st.write("#### Graph explanation:")
    st.markdown('''In this graph, I illustrate the available percentage of different rooms at different checking time.
    So you can see the available percetage of one room at different hours throughtout a period of time.   
    For example, you can see the percentage of availability of room 257 go up and down from 28 Nov to 10 Dec (you can change the
    time period to whatever you like) 
    
    ''')



def Graph_3():
    st.markdown('## 3. The average availability of rooms  ')
    st.write('##### The graph below shows the average availability of rooms in one day')

    # Select the date you want to view
    date = st.date_input(
        'Select the date you want to view',
        DEFAULT_START_TIME,
        min_value=DEFAULT_START_TIME,
        key='lol'
    )

    query = '''
    SELECT  room,
            checking_date,
            ROUND(AVG(available_percent),2) AS average_rate
            
    FROM 
    (SELECT	checking_date,
        HOUR(checking_time) AS checking_hour,
        room,
                COUNT(status) AS total_cnt,
        SUM(CASE
        WHEN status = 'Available' THEN 1
        ELSE 0
        END) AS available_cnt,
        (SUM(CASE
        WHEN status = 'Available' THEN 1
        ELSE 0
        END)/ COUNT(status) ) * 100 AS available_percent

    FROM library_schedule
    WHERE checking_date = "{date}"
    GROUP BY checking_date, checking_hour, room) AS table_1
    GROUP BY room
    ORDER by room

    ;
    
    '''.format(date = str(date))

    # Now get the df from query and print it out
    df = QueryToDataframe(query=query )
    PrintDataframeStreamlit(df = df)

    plot = px.bar(df, x='room', y = 'average_rate',
                    text='average_rate', orientation='v', 
                    opacity= 0.9,
                    width=800, height=700,
                    title= "Avarage percent of availability of different room on a day"
                    )
    plot.update_traces(textangle=0,textposition="outside")
    st.plotly_chart(plot )
    st.write("#### Graph explanation:")
    st.markdown('''
    In this graph, I calculate the average percentage of availability of different rooms in a day. So if room 257 has the 
    average rate of 15.7, that means on average (between different checking_hour) 15.75 percent of time the room is empty.

    ''')




def main():
    # Instruction to my app
    st.title("WELCOME TO MY APP")
    

    # Now get the whole database, just to see, lol
    st.write("##### The original dataset")
    st.write("This is the first 1000 lines of the dataset in database")
    query_full_table = '''
        SELECT  checking_date, checking_time,  
                room_hour, day_of_week, 
                room, status
        FROM library_schedule 
        ORDER checking_date DESC
        LIMIT 1000;
    '''
    df = QueryToDataframe(query=query_full_table,columns_to_convert=['checking_time', 'room_hour'])

    # Now print that shit to streamlit
    PrintDataframeStreamlit(df=df)

    # Now explain the table
    st.write("#### Columns explanation:")
    st.write("*checking_date*: the library schedule of that day")
    st.write("*checking_time*: the time I scrap the webiste (hourly)")
    st.write("*room_hour*: the library schedule at that time (schedule is distrubuted as 15 min blocks) ")
    st.write("*room*: room number")
    st.write("*status*: the status of the library room at a specific time and a scecific day, can be available and unavailable")

    # Graph 1 - Avaialability của từng phòng vào từng h khác nhau
    # Chia database theo ngày (tức là cho người ta select ngày nào á)
    Graph_1()

    # Graph 2
    Graph_2()

    # GRAPH 3
    Graph_3()

    # Graph 4
    




if __name__ == "__main__":
    main()
