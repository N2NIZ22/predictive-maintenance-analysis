import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# importing the data
data = pd.read_csv("predictive_maintenance.csv")

# sqlite3 setup
conn = sqlite3.connect(":memory:")
data.to_sql('machines',conn, index=False)

# Table Info
table_info = pd.read_sql_query("""SELECT * FROM pragma_table_info("machines")""", conn)
print(table_info)

# Failure summary
fail_sum = pd.read_sql("""SELECT "Failure Type", COUNT(*) as amount, 
                        AVG("Torque [Nm]") as avg_torque, AVG("Rotational speed [rpm]") as avg_rpm,
                        AVG("Tool wear [min]") as avg_tool_wear FROM machines 
                        GROUP BY "Failure Type" 
                        ORDER BY amount DESC
                        """, conn)
print(fail_sum)

# Average by target
average_tar = pd.read_sql_query("""SELECT "Target", COUNT(*) as amount, 
                                AVG("Air temperature [K]") as avg_air_temp,
                                AVG("Process temperature [K]") as avg_proc_temp,
                                AVG("Rotational speed [rpm]") as avg_rpm,
                                AVG("Tool wear [min]") as avg_tool_wear,
                                AVG("Torque [Nm]") as avg_torque
                                FROM machines
                                GROUP BY "Target" """, conn)
print(average_tar)

# Failure rate

fail_rate = pd.read_sql_query("""SELECT ROUND(AVG("Target")*100, 2) as failure_rate 
                                FROM machines""", conn)
print(fail_rate)

fail_rate_type = pd.read_sql_query("""SELECT "Type", ROUND(AVG("Target")*100, 2) as fail_rate,
                                      COUNT(*) as amount
                                      FROM machines
                                      GROUP BY "Type" """
                                   , conn)
print(fail_rate_type)

# Tool wear above average
tool_wear = pd.read_sql_query("""SELECT "Tool wear [min]" > (SELECT AVG("Tool wear [min]") FROM machines)
                                as above_avg, COUNT(*) as amount,
                                ROUND(AVG("Target")*100, 2) as failure_rate_pct
                                FROM machines
                                GROUP BY above_avg """, conn)
print(tool_wear)

# Comparing failure rate per Type with overall rate
failure_rate = pd.read_sql_query("""WITH overall_rate AS (SELECT ROUND(AVG("Target")*100, 2) as overall
                                                       FROM machines)
                                    SELECT "Type", ROUND(AVG("Target")*100, 2) as fail_rate, 
                                    MAX(overall_rate.overall) as overall 
                                    FROM machines
                                    CROSS JOIN overall_rate
                                    GROUP BY "Type"
                                    """, conn)
print(failure_rate)

# Window functions on tool wear
ranked = pd.read_sql_query("""SELECT *, 
                                    RANK() OVER (PARTITION BY "Type" ORDER BY "Tool wear [min]" DESC) AS rank,
                                    ROW_NUMBER() OVER (PARTITION BY "Type" ORDER BY "Tool wear [min]" DESC) AS row_num,
                                    DENSE_RANK() OVER (PARTITION BY "Type" ORDER BY "Tool wear [min]" DESC) AS dense_rank
                              FROM machines
                              ORDER BY "Type", "Tool wear [min]" DESC
                              LIMIT 20""", conn)
print(ranked)

highest_torque = pd.read_sql_query("""WITH highest_torque AS (SELECT *, 
                                                                     ROW_NUMBER() OVER (PARTITION BY "Type"
                                                                                       ORDER BY "Torque [Nm]" DESC) AS rn
                                                               FROM machines) 
                                      SELECT * FROM highest_torque
                                      WHERE rn=1""", conn)
print(highest_torque)

above_avg = pd.read_sql_query("""SELECT "Product ID", "Type", "Tool wear [min]",
                                         ROUND(AVG("Tool wear [min]") OVER (PARTITION BY "Type"), 2) as avg_wear,
                                         ROUND("Tool wear [min]"-AVG("Tool wear [min]") OVER (PARTITION BY "Type"), 2) as diff_from_avg
                                FROM machines
                                ORDER BY diff_from_avg DESC
                                LIMIT 20""", conn)
print(above_avg)

# Failure rate by Tool wear band
wear_band_rates = pd.read_sql_query("""SELECT CASE 
                                                WHEN "Tool wear [min]" < 60 THEN 'low (0-59)'
                                                WHEN "Tool wear [min]" < 120 THEN 'medium (60-119)'
                                                WHEN "Tool wear [min]" < 200 THEN 'high (120-199)'
                                                WHEN "Tool wear [min]" < 230 THEN 'extreme (200-229)'
                                                ELSE 'danger (230+)'
                                             END AS wear_band,
                                             COUNT(*) AS amount,
                                             ROUND(AVG("Target")*100,2) AS fail_rate_pct
                                       FROM machines
                                       GROUP BY wear_band
                                       ORDER BY MIN("Tool wear [min]")""", conn)
print(wear_band_rates)

# Failure rate by Torque band
torque_band_rates = pd.read_sql_query("""SELECT CASE
                                                   WHEN "Torque [Nm]" < 20 THEN 'low (0-19)'
                                                   WHEN "Torque [Nm]" < 40 THEN 'medium (20-39)'
                                                   WHEN "Torque [Nm]" < 55 THEN 'high (40-54)'
                                                   WHEN "Torque [Nm]" < 65 THEN 'extreme (55-64)'
                                                   ELSE 'danger (65+)'
                                                   END AS torque_band,
                                                COUNT(*) AS amount,
                                                ROUND(AVG("Target")*100,2) AS fail_rate_pct
                                          FROM machines
                                          GROUP BY torque_band
                                          ORDER BY MIN("Torque [Nm]")""", conn)
print(torque_band_rates)

# sanity check
flag_no_type = pd.read_sql_query("""SELECT COUNT(*) AS amount
                                    FROM machines
                                    WHERE "Target"= 1
                                    AND "Failure Type" = 'No Failure' """, conn)
print(flag_no_type)

type_no_flag = pd.read_sql_query("""SELECT "Failure Type", COUNT(*) AS amount
                                    FROM machines
                                    WHERE "Target" = 0
                                    AND "Failure Type" != 'No Failure'
                                    GROUP BY "Failure Type" """, conn)
print(type_no_flag)