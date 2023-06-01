from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None



def check_password(password):
    # Check 1: has to be at least 8 characters
    if len(password) < 8:
        print("Password must be 8 characters or more, try again!")
        return False

    # Check 2: must have both uppercase and lowercase
    if not (password.islower() == False and password.isupper() == False):
        print("Password must have both uppercase and lowercase characters, try again!")
        return False

    #Check 3: must be alphanumeric

    if not (password.isalpha() == False and password.isnumeric() == False):
        print("Password must have both letters and numbers, try again!")
        return False

    #Check 4: must have special characters
    flag = False
    characters = ['!', '@', '#', '?']

    for character in password:
        if character in characters:
            flag = True
            break
    #print(f"flag is {flag}")
    if not flag:
        print("Password must contain at least one special character, try again!")
        return False

    return True





def create_patient(tokens):
    """
    TODO: Part 1
    """
    #create_patient <username> <password>
    #check 1: the length for tokens need to be exactly 3 to include all information

    if len(tokens) != 3:
        print('Failed to create user.')
        return

    username = tokens[1]
    password = tokens[2]

    #check 2: check if username has already been taken

    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # Check 3: Check if the password is strong or not

    if check_password(password) is False:
        return

    #create the patient
    patient = Patient(username, salt=salt, hash=hash)

    #save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error: ", e)
        quit()

    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user : ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # Check 3: Check if password is strong or not
    if check_password(password) == False:
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


# def username_exists_patient(username):
#     cm = ConnectionManager()
#     conn = cm.create_connection()
#
#     select_username = "SELECT * FROM Patients WHERE Username = %s"
#     try:
#         cursor = conn.cursor(as_dict=True)
#         cursor.execute(select_username, username)
#         #returns false if the cursor is not before the first record or if there are not rows in the ResultSet.
#         for row in cursor:
#             return row['Username'] is not None
#
#     except pymssql.Error as e:
#         print("Error occured when checking username")
#         print("Db-Error:", e)
#         quit()
#
#     except Exception as e:
#         print("Error occurred when checking username")
#         print("Error:", e)
#     finally:
#         cm.close_connection()
#     return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    #login_patient <username> <password>
    #check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    #check 2: the length for tokens need to be exactly 3 to include all information
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None

    try:
        patient = Patient(username, password=password).get()

    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()

    except Exception as e:
        print("Login failed.")
        print("Error: ", e)
        return

    # check if the login was successful
    if patient is None:
        print("Failed to login")
    else:
        print("Logged in as: " + username)
        current_patient = patient


    #pass


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    #search_caregiver_schedule <date>
    #Check1 : check if someone is logged in or not
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    #Check 2: the length of the tokens needs to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    temp = tokens[1]
    #Check 3: Check if the format of the date is MM-DD-YYY
    if temp[2] != "-" or temp[5] != "-" or len(temp) != 10:
        print("Date must be in MM-DD-YYYY format, try again!")
        return

    date = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()

    available = "SELECT Username FROM Availabilities WHERE Time = CONVERT(DATETIME, %s) ORDER BY Username"


    try:
        cursor = conn.cursor()
        cursor.execute(available, date)
        print("Please find available caregivers below \n")
        for row in cursor:
            print(row[0])

    except pymssql.Error as e:
        print("Error")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again")
        print("Error:", e)

    vaccine = "SELECT * FROM Vaccines"
    try:
        cursor = conn.cursor()
        cursor.execute(vaccine)
        print("Please find available vaccines below \n")
        for row in cursor:
            print(row[0], " ", row[1])
            return
    except pymssql.Error as e:
        print("Error")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()
    #pass


def reserve(tokens):
    """
    TODO: Part 2
    """
    #reserve <date> <vaccine>
    #Check 1: the lenght for the tokens need to be exactly 2 to include all information including operation name
    if len(tokens) != 3:
        print("Please try again!")
        return

    #Check 2: check the date format
    temp = tokens[1]
    if temp[2] != "-" or temp[5] != "-" or len(temp) != 10:
        print("The date format must be MM-DD-YYYY, please try again!")
        return

    #Check 3: check if someone is logged in or not
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    #Check 4: check if the logged in user is a patient or not
    if current_patient is None and current_caregiver is not None:
        print("Please login as a patient, not caregiver!")
        return

    date = tokens[1]
    vaccine_name = tokens[2]
    caregiver_assgnd = None

    #Get available caregiver
    cm = ConnectionManager()
    conn = cm.create_connection()
    chosen_caregiver = "SELECT TOP 1 Username FROM Availabilities WHERE Time = CONVERT(DATETIME, %s) ORDER BY Username"
    try:
        cursor = conn.cursor()
        cursor.execute(chosen_caregiver, date)
        for row in cursor:
            caregiver_assgnd = row[0]

        if caregiver_assgnd is None:
            print("No caregiver is available")
            return
    except pymssql.Error as e:
        print("Error")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()

    # Now get the available vaccines
    cm = ConnectionManager()
    conn = cm.create_connection()
    doses_query = "SELECT Doses FROM Vaccines WHERE Name = %s"
    try:
        cursor = conn.cursor()
        cursor.execute(doses_query, (vaccine_name))
        doses = []
        for row in cursor:
            #print("Ran")
            doses_needed = int(row[0])
            doses.append(doses_needed)
        #check if we have enough doses
        if len(doses) == 0:
            doses_needed = 0
            print("Not enough available doses!")
            return

    except pymssql.Error as e:
        print("Error")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()

    #Get the appointment ID
    cm = ConnectionManager()
    conn = cm.create_connection()
    appt = "SELECT TOP 1 Appointment_id FROM Appointments ORDER BY Appointment_id DESC"
    try:
        cursor = conn.cursor()
        cursor.execute(appt)
        appt_list = []
        for row in cursor:
            appt_id = int(row[0])
            appt_list.append(appt_id)
        if len(appt_list) == 0:
            appt_id = 0
    except pymssql.Error as e:
        print("Error")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()

    #Update the Availabilites table
    vaccine = Vaccine(tokens[2], doses_needed)
    cm = ConnectionManager()
    conn = cm.create_connection()
    #print("Ran")
    deletion_query = "DELETE FROM Availabilities WHERE Username IN" \
                     "(SELECT TOP 1 Username FROM Availabilities WHERE Time = CONVERT(DATETIME, %s) ORDER BY Username)" \
                     "AND Time = CONVERT(DATETIME, %s)"

    try:
        #print("Ran this")
        cursor = conn.cursor()
        cursor.execute(deletion_query, (date, date))
        conn.commit()
        appt_id += 1
        vaccine.decrease_available_doses(1)
    except pymssql.Error as e:
        print("Error")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()
    print(f"Appointment ID:{int(appt_id)}\nCaregiver username:{caregiver_assgnd}")

    #Update the appointments table
    cm = ConnectionManager()
    conn = cm.create_connection()
    appt_query = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, CONVERT(DATETIME, %s))"
    try:
        cursor = conn.cursor()
        cursor.execute(appt_query, (appt_id, current_patient.username, caregiver_assgnd, vaccine_name, date))
        conn.commit()
    except pymssql.Error as e:
        print("Error")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()

    #pass


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    #Check 1: the length of tokens needs to be exactly 1
    if len(tokens) != 1:
        print("Please try again!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    if current_caregiver is not None:
        query = "SELECT Appointment_id, Vaccine_name AS vaccine_name , Time AS date , Patient_username AS patient_name " \
                                   "FROM Appointments " \
                                   "WHERE Caregiver_username = %s " \
                                   "ORDER BY Appointment_id"
        try:
            cursor1 = conn.cursor()
            cursor1.execute(query, current_caregiver.username)
            for row in cursor1:
                print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}")
            return
        except pymssql.Error as e:
            print("Error")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Please try again!")
            print("Error:", e)
        finally:
            cm.close_connection()

    else:
        query = "SELECT Appointment_id, Vaccine_name AS vaccine_name, Time AS date, Caregiver_username AS caregiver_name " \
                                 "FROM Appointments " \
                                 "WHERE Patient_username = %s " \
                                 "ORDER BY Appointment_id"

        try:
            cursor2 = conn.cursor()
            cursor2.execute(query, current_patient.username)
            for row in cursor2:
                print(f"{row[0]}, {row[1]}, {row[2]}, {row[3]}")
            return
        except pymssql.Error as e:
            print("Error")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Please try again!")
            print("Error:", e)
        finally:
            cm.close_connection()

    #pass


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver

    # Check if a user is currently logged in
    if current_patient is None and current_caregiver is None:
        print("No user is currently logged in.")
        return

    # Log out the current user
    if current_patient is not None:
        print("Logged out user:", current_patient.username)
        current_patient = None
    elif current_caregiver is not None:
        print("Logged out user:", current_caregiver.username)
        current_caregiver = None


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        # response = response.lower()
        response = response
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
