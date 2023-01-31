# -*- coding: utf-8 -*-
"""
This script obtains information about quality of code from SonarQube
Created on 25.ENE.2023

@author: Byron Nizo
         David Caicedo
"""
import http.client
import urllib.parse
import json
import csv
from csv import writer
from google.cloud import bigquery
import os
import datetime
import pandas
import pytz


lismicros=[ ]
listbranch=[ ]
listname=[ ]
listnum = []

project_list= [
      {'branch':'master', 'name':'cataloge'}
    , {'branch':'master', 'name':'ecommerce:checkout-api'}
    , {'branch':'master', 'name':'ads-api'}
    , {'branch':'master', 'name':'order-tracking-api'}
    , {'branch':'master', 'name':'shop-cart'}
    , {'branch':'master', 'name':'timewindow-api'}
    , {'branch':'master', 'name':'ads-api'}
    , {'branch':'master', 'name':'ms-authenticator'}
    , {'branch':'master', 'name':'ms-geo'}
    , {'branch':'master', 'name':'ms-user'}
    , {'branch':'master', 'name':'notification-api'}
    , {'branch':'master', 'name':'vendor-coverage'}
    , {'branch':'main', 'name':'ms-search-bar'}
   
    ]

fields= [
      'period'
    , 'metrics'
    ]

metrics= [
      'bugs'
    , 'vulnerabilities'
    , 'security_hotspots'
    , 'code_smells'
    , 'coverage'
    , 'duplicated_lines_density'
    ]


def getQualityGates(conn, project, branch)->str:
    url = getURL('/api/measures/component', {
        'additionalFields': ','.join(fields),
        'metricKeys': ','.join(metrics),
        'branch': branch,
        'component': project
        })
    
    conn.request("GET", url, '', headers)
    response = conn.getresponse()
    data = response.read()
    
    printQualityGates(project, branch, json.loads(data))

    
    #print("URL: " + url)    
    #print("Project: " + project)
    #print(data)
    

def printQualityGates(project, branch, data):
    
    try:
        if hasattr(data, 'errors'):
            for e in data['errors']:
                print(f"ERROR|{e['msg']}||")
            return
        
    
        for x in data['component']['measures']:
            print(f"{project}|{branch}|{x['metric']}|{x['value']}")
            metrica={x['metric']}
            valor={x['value']}
                        
            lismicros.append(project)
            listbranch.append(branch)
            listname.append(metrica)
            listnum.append(valor)
            #print(listname) 
            #print(listnum)   

            #print(lismicros)

            
    except:
        print(f"ERROR|{data}||")
        
    
    
    """
    #VERSION ANTERIOR
    print(f"\n\n.: {project} . {branch} :.")
    
    try:
        if hasattr(data, 'errors'):
            print("---> ERROR")
            for e in data['errors']:
                print('---> ' + e['msg'])
            return
        
    
        for x in data['component']['measures']:
            print(f"{x['metric']} : {x['value']}")
            
    except:
        print("---> UNKNOWN ERROR!")
        print(data)
        
    """
    

def getURL(path, data)->str:
    return f"{path}?{urllib.parse.urlencode(data)}"


headers = {
    'accept': 'application/json'
  , 'accept-language': 'es-ES,es;q=0.9'
  , 'Authorization': 'Basic ZWQxYjc3OWNmMDgyYWVkODY4ODAyZDVlOGI2NmQ4NGFkNmMwMDFlNzo='
}

conn = http.client.HTTPSConnection("sonar.chiper.co")

try:
    conn.connect()
    for project in project_list:
        getQualityGates(conn, project['name'], project['branch'])
        
finally:
    conn.close




os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./key.json"
PROJECT_ID = 'dataflow-chiper'
filename = 'datossonar.csv' # this is the file path to your csv
dataset_id = 'Devops'
table_id = 'infosonar2'
table2_id = "dataflow-chiper.Devops.tablesonar"
# create a client instance for your project
client = bigquery.Client(project=PROJECT_ID, location="US")
table_id = "dataflow-chiper.Devops.infosonar2"
query = f""" DELETE FROM `dataflow-chiper.Devops.infosonar2` WHERE TRUE"""
query_job = client.query(query)
for lismicros, listbranch, listname, listnum in zip(lismicros, listbranch, listname, listnum):
        test=str(listname)
        test2=test.replace('{','').replace('}','')
        test3=eval(test2)
        #print(te)
        nametest1=str(listnum)
        nametest2=nametest1.replace('{','').replace('}','')
        nametest3=eval(nametest2)
        #writer.writerow({'Microservice': lismicros,
         #                'Branch': listbranch,
          #               'name' : test3,
           #              'number' : nametest3,
            #             })

# # records = [{'Microservice': lismicros,
# #             'Branch': listbranch,
# #             'name' : test3,
# #             'number' : nametest3,  
        records = [{'Microservice': lismicros,
                    'Branch': listbranch,
                    'name' : test3,
                    'number' : nametest3,  
                    }]


        dataframe = pandas.DataFrame(
            records,
            # In the loaded table, the column order reflects the order of the
            # columns in the DataFrame.
            columns=[
                "Microservice",
                "Branch",
                "name",
                "number",
                
            ],
        )
        
        job_config = bigquery.LoadJobConfig(
             # Specify a (partial) schema. All columns are always written to the
             # table. The schema is used to assist in data type definitions.
             schema=[
        #         # Specify the type of columns whose type cannot be auto-detected. For
        #         # example the "title" column uses pandas dtype "object", so its
        #         # data type is ambiguous.
        #         # Indexes are written if included in the schema by name.
                 bigquery.SchemaField("Microservice", bigquery.enums.SqlTypeNames.STRING),
                 bigquery.SchemaField("Branch", bigquery.enums.SqlTypeNames.STRING),
                 bigquery.SchemaField("name", bigquery.enums.SqlTypeNames.STRING),
                 bigquery.SchemaField("number", bigquery.enums.SqlTypeNames.STRING),
             ],
        #     # Optionally, set the write disposition. BigQuery appends loaded rows
        #     # to an existing table by default, but with WRITE_TRUNCATE write
        #     # disposition it replaces the table with the loaded data.
        #     #write_disposition="WRITE_TRUNCATE",
         )

        job = client.load_table_from_dataframe(
            dataframe, table_id, job_config=job_config
        )  # Make an API request.
        job.result()  # Wait for the job to complete.

        table = client.get_table(table_id)  # Make an API request.
        print(
            "Loaded {} rows and {} columns to {}".format(
                table.num_rows, len(table.schema), table_id
            )
        )