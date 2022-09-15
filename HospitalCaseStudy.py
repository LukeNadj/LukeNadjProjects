import simpy as sm
import math
import random
import matplotlib.pyplot as plt

class Qstats:
    def __init__(self, show_full_output = True, show_validation_output = True):
        self.show_full_output = show_full_output
        self.show_validation_output = show_validation_output
        if self.show_validation_output:
            print('patient,cat,tot_stay,resus_dr_wait,resus_room_wait,triage_wait,bed_wait,consult_wait,treat_wait')

        #Number of patients discharged
        self.CAT1dis = 0
        self.CAT2dis = 0
        self.CAT3dis = 0
        self.dis_tot = 0

        #Current patient number (For validation)
        self.CurrentPatient = 0

        #Total stay time for patients
        self.CAT1_stay_time_tot = 0
        self.CAT2_stay_time_tot = 0
        self.CAT3_stay_time_tot = 0

        #Wait for resus rooms, Average wait
        self.resus_wait_tot = 0

        #Wait for resus doctor
        self.doc_wait_resus_tot = 0

        #Wait for beds
        self.CAT2_bed_wait_tot = 0
        self.CAT3_bed_wait_tot = 0

        #Wait for consult doctor
        self.CAT2_doc_wait_consult_tot = 0
        self.CAT3_doc_wait_consult_tot = 0

        #Wait for treatment doctor
        self.CAT2_doc_wait_treat_tot = 0
        self.CAT3_doc_wait_treat_tot = 0

        #Patients diverted
        self.patients_diverted = 0

        #Resus room utilisation
        self.resus_util = 0

        #Beds utilisation
        self.bed_util = 0

        #Doctor utilisation
        self.doc_util = 0

        #Waiting room utilisation
        self.wait_util = 0

        #constants used to indicate CAT
        self.CAT1 = 1
        self.CAT2 = 2
        self.CAT3 = 3
        self.DIVERTED = 0

        #Constants used to indicate event_type
        self.ARRIVE = 4
        self.DOCTOR = 5
        self.RESUS = 6
        self.DOCTOR_END = 7
        self.BED = 8
        self.OBS_END = 9
        self.DOCTOR_TREAT = 10
        self.DOCTOR_TREAT_END = 11
        
    def patient_num(self):
        self.CurrentPatient += 1
        
    #timestamps is a list of increasing length consisting of [t_arrival, t_doc_start, t_resus_start, t_depart] for CAT1
    #For CAT2/3, timestamps = [t_arrival, t_triage, t_triage_end, t_bed, t_doc1, t_doc1_end, t_obs_end, t_doc2, t_doc2_end]
    def notify_event(self, CAT, timestamps):
        t = max(timestamps)
        #Min 435 Max 4785
        #if self.CurrentPatient >= 435 and self.CurrentPatient <= 4785:
        if CAT == self.CAT1:
            self.CAT1dis += 1
            self.CAT1_stay_time_tot += timestamps[3] - timestamps[0]
            self.doc_wait_resus_tot += timestamps[1] - timestamps[0]
            self.resus_wait_tot += timestamps[2] - timestamps[1]
            self.resus_util += timestamps[3] - timestamps[2]
            self.doc_util += timestamps[3] - timestamps[1]

        elif CAT == self.CAT2:
            self.CAT2dis += 1
            self.CAT2_stay_time_tot += timestamps[8] - timestamps[0]
            self.CAT2_bed_wait_tot += timestamps[3] - timestamps[2]
            self.CAT2_doc_wait_consult_tot += timestamps[4] - timestamps[3]
            self.CAT2_doc_wait_treat_tot += timestamps[7] - timestamps[6]
            self.bed_util += timestamps[8] - timestamps[3]
            self.doc_util += (timestamps[5] - timestamps[4]) + (timestamps[8] - timestamps[7])
            self.wait_util += timestamps[3] - timestamps[2]

        elif CAT == self.CAT3:
            self.CAT3dis += 1
            self.CAT3_stay_time_tot += timestamps[8] - timestamps[0]
            self.CAT3_bed_wait_tot += timestamps[3] - timestamps[2]
            self.CAT3_doc_wait_consult_tot += timestamps[4] - timestamps[3]
            self.CAT3_doc_wait_treat_tot += timestamps[7] - timestamps[6]
            self.bed_util += timestamps[8] - timestamps[3]
            self.doc_util += (timestamps[5] - timestamps[4]) + (timestamps[8] - timestamps[7])
            self.wait_util += timestamps[3] - timestamps[2]

        elif CAT == self.DIVERTED:
            self.patients_diverted += 1                                 

    def validate_event(self, patient_id, CAT, timestamps):
    #patient,cat,tot_stay,resus_dr_wait,resus_room_wait,triage_wait,bed_wait,consult_wait,treat_wait
        if self.show_validation_output:
            if CAT == self.CAT1:
                tot_stay = timestamps[3] - timestamps[0]
                resus_dr_wait = timestamps[1] - timestamps[0]
                resus_room_wait = timestamps[2] - timestamps[1]
                triage_wait = 0
                bed_wait = 0
                consult_wait = 0
                treat_wait = 0
                
            elif CAT == self.CAT2:
                tot_stay = timestamps[8] - timestamps[0]
                resus_dr_wait = 0
                resus_room_wait = 0
                triage_wait = timestamps[1] - timestamps[0]
                bed_wait = timestamps[3] - timestamps[2]
                consult_wait = timestamps[4] - timestamps[3]
                treat_wait = timestamps[7] - timestamps[6]

            elif CAT == self.CAT3:
                tot_stay = timestamps[8] - timestamps[0]
                resus_dr_wait = 0
                resus_room_wait = 0
                triage_wait = timestamps[1] - timestamps[0]
                bed_wait = timestamps[3] - timestamps[2]
                consult_wait = timestamps[4] - timestamps[3]
                treat_wait = timestamps[7] - timestamps[6]

            print(str(patient_id) + ',',str(CAT)+',','%.2f,' % tot_stay,'%.2f,' % resus_dr_wait,'%.2f,' % resus_room_wait,\
                  '%.2f,' % triage_wait,'%.2f,' % bed_wait,'%.2f,'% consult_wait,'%.2f,' % treat_wait)
        
    def print_event(self, patient_id, CAT, event_type, doc_choice, time) :
        if self.show_full_output:
            if event_type == self.ARRIVE:
                print('CAT', CAT,' patient# ', patient_id, ' arrived at ', time)
            elif event_type == self.DOCTOR:
                print('CAT', CAT,' patient# ', patient_id, ' got doctor ', doc_choice, ' at time ', time)
            elif event_type == self.DOCTOR_END:
                print('CAT', CAT,' patient# ', patient_id, ' finished with doctor ', doc_choice, ' at time ', time)
            elif event_type == self.RESUS:
                print('CAT', CAT,' patient# ', patient_id, ' got Resus Room at time ', time)
            elif event_type == self.BED:
                print('CAT', CAT,' patient# ', patient_id, ' got bed at time ', time)
            elif event_type == self.OBS_END:
                print('CAT', CAT,' patient# ', patient_id, ' finished observing at time ', time)
            elif event_type == self.DOCTOR_TREAT:
                print('CAT', CAT,' patient# ', patient_id, ' got doctor (treatment) ', doc_choice, ' at time ', time)
            elif event_type == self.DOCTOR_TREAT_END:
                print('CAT', CAT,' patient# ', patient_id, ' finished with doctor (treatment) ', doc_choice, ' at time ', time)
            elif event_type == self.DIVERTED:
                print('CAT', CAT,' patient# ', patient_id, ' diverted')
    
    def display_summary_stats(self, t_max, resus_rooms, doctors, beds, waiting_room):
        #self.update_queue_and_system_counts(t_max, 0)
        self.dis_tot = self.CAT1dis + self.CAT2dis + self.CAT3dis
        print('Average throughput for CAT1 patients = %.2f' % (self.CAT1dis / t_max * 60))
        print('Average throughput for CAT2 patients = %.2f' % (self.CAT2dis / t_max * 60))
        print('Average throughput for CAT3 patients = %.2f' % (self.CAT3dis / t_max * 60))

        print('Average length of stay for CAT1 patients = %.2f' % (self.CAT1_stay_time_tot / self.CAT1dis))
        print('Average length of stay for CAT2 patients = %.2f' % (self.CAT2_stay_time_tot / self.CAT2dis))
        print('Average length of stay for CAT3 patients = %.2f' % (self.CAT3_stay_time_tot / self.CAT3dis))

        print('Average wait for resus doctor = %.2f' % (self.doc_wait_resus_tot / self.CAT1dis))
        print('Average wait for resus room = %.2f' % (self.resus_wait_tot / self.CAT1dis))
        
        print('Average bed wait for CAT2 patients = %.2f' % (self.CAT2_bed_wait_tot / self.CAT2dis))
        print('Average bed wait for CAT3 patients = %.2f' % (self.CAT3_bed_wait_tot / self.CAT3dis))

        print('Average consult doctor wait for CAT2 patients = %.2f' % (self.CAT2_doc_wait_consult_tot / self.CAT2dis))
        print('Average consult doctor wait for CAT3 patients = %.2f' % (self.CAT3_doc_wait_consult_tot / self.CAT3dis))

        print('Average treat doctor wait for CAT2 patients = %.2f' % (self.CAT2_doc_wait_treat_tot / self.CAT2dis))
        print('Average treat doctor wait for CAT3 patients = %.2f' % (self.CAT3_doc_wait_treat_tot / self.CAT3dis))

        print('Proportion of patients diverted = %.2f' % (self.patients_diverted / (self.dis_tot + self.patients_diverted) * 100), '%')
        print('Resus room utilisation = %.2f' % (self.resus_util / (resus_rooms * t_max) * 100), '%')
        print('Doctor utilisation = %.2f' % (self.doc_util / (doctors * t_max) * 100), '%')
        print('Bed utilisation = %.2f' % (self.bed_util / (beds * t_max) * 100), '%')
        print('Wait room utilisation = %.2f' % (self.wait_util / (waiting_room * t_max) * 100), '%')


def arrivals(env, CAT, arrival_rate, triage, resus, consult, observe, treat, doctors, resus_rooms, nurses, beds, waiting_room_max, qstats):
    i = 0
    while True:
        i += 1
        iat = random.expovariate(arrival_rate)  #sample interarrival time
        treatment_time = random.triangular(treat[0], treat[2], treat[1])    #Sample treatment time
        yield env.timeout(iat) #advance to arrival time
        if CAT == 1:
            treatment_time = random.triangular(resus[0], resus[2], resus[1])
            env.process(CAT1(env, i, treatment_time, doctors, resus_rooms, qstats))
        elif CAT == 2:
            triage_time = random.triangular(triage[0], triage[2], triage[1])
            consultation_time = random.triangular(consult[0], consult[2], consult[1])
            observe_time = random.triangular(observe[0], observe[2], observe[1])
            env.process(CAT2(env, i, triage_time, consultation_time, observe_time,\
                             treatment_time, doctors, nurses, beds, waiting_room_max, qstats))
        elif CAT == 3:
            triage_time = random.triangular(triage[0], triage[2], triage[1])
            consultation_time = random.triangular(consult[0], consult[2], consult[1])
            observe_time = random.triangular(observe[0], observe[2], observe[1])
            env.process(CAT3(env, i, triage_time, consultation_time, observe_time,\
                             treatment_time, doctors, nurses, beds, waiting_room_max, qstats))

def CAT1(env, patient_id, treatment_time, doctors, resus_rooms, qstats):

    qstats.patient_num()
    CurrentPatient = qstats.CurrentPatient  #Determines what number the patient is
    t_arrive = env.now
    qstats.print_event(patient_id, qstats.CAT1, qstats.ARRIVE, 0, t_arrive)

    doc_req = []
    for i in range(len(doctors)):
        doc_req.append(doctors[i].request(priority = 1))

    doc_chosen = yield env.any_of(doc_req)  #Queue for all doctors, yield the first and cancel the rest

    doc_list = list(doc_chosen.keys())
    first_doc = doc_list[0]

    for j in range(len(doc_req)):   #This loop cancels all other doctors after one has been selected
        if first_doc == doc_req[j]:
            choice = j
            for k in range(len(doc_req)):
                if k != j:
                    if doc_req[k] in doc_list:
                        doctors[k].release(doc_req[k])
                    else:
                        doc_req[k].cancel()
            break                
    
    t_doc = env.now
    qstats.print_event(patient_id, qstats.CAT1, qstats.DOCTOR, choice, t_doc)
    
    resus_request = resus_rooms.request()   #Queue for resus room
    yield resus_request
    t_resus = env.now
    qstats.print_event(patient_id, qstats.CAT1, qstats.RESUS, choice, t_resus)
    
    yield env.timeout(treatment_time)
    t_depart = env.now
    
    doctors[choice].release(doc_req[choice])
    resus_rooms.release(resus_request)
    qstats.print_event(patient_id, qstats.CAT1, qstats.DOCTOR_END, choice, t_depart)

    timestamps = [t_arrive, t_doc, t_resus, t_depart]   #Stats notifications
    qstats.notify_event(qstats.CAT1, timestamps)
    qstats.validate_event(CurrentPatient, qstats.CAT1, timestamps)
    
def CAT2(env, patient_id, triage_time, consultation_time, observe_time, treatment_time, doctors, nurses, bed, waiting_room_max, qstats):

    qstats.patient_num()
    CurrentPatient = qstats.CurrentPatient
    
    t_arrive = env.now
    qstats.print_event(patient_id, qstats.CAT2, qstats.ARRIVE, 0, t_arrive)
    
    triage_request = nurses.request()   #Patient sees triage nurse
    yield triage_request
    t_triage = env.now
    env.timeout(triage_time)
    nurses.release(triage_request)
    t_triage_end = env.now

    if len(bed.queue) == (waiting_room_max):    #Check to see if waiting room is ful
        timestamps = [t_arrive, t_triage_end]
        qstats.notify_event(qstats.DIVERTED, timestamps)
        qstats.print_event(patient_id, qstats.CAT2, qstats.DIVERTED, 0, 0)
    
    else:
        bed_request = bed.request(priority = 2)     #Patient waits for a bed
        yield bed_request
        t_bed = env.now
        qstats.print_event(patient_id, qstats.CAT2, qstats.BED, 0, t_bed)

        doc_req = []    #Queue for all doctors, cancel all except the first 
        for i in range(len(doctors)):
            doc_req.append(doctors[i].request(priority = 4))

        doc_chosen = yield env.any_of(doc_req)

        doc_list = list(doc_chosen.keys())
        first_doc = doc_list[0]

        for j in range(len(doc_req)):
            if first_doc == doc_req[j]:
                choice = j
                for k in range(len(doc_req)):
                    if k != j:
                        if doc_req[k] in doc_list:
                            doctors[k].release(doc_req[k])
                        else:
                            doc_req[k].cancel()
                break

        t_doc1 = env.now
        qstats.print_event(patient_id, qstats.CAT2, qstats.DOCTOR, choice, t_doc1)

        yield env.timeout(consultation_time)    #Consultation time
        t_doc1_end = env.now
        qstats.print_event(patient_id, qstats.CAT2, qstats.DOCTOR_END, choice, t_doc1_end)

        doctors[choice].release(doc_req[choice])

        yield env.timeout(observe_time)     #Observation time
        t_obs_end = env.now
        qstats.print_event(patient_id, qstats.CAT2, qstats.OBS_END, choice, t_obs_end)

        doctor_request2 = doctors[choice].request(priority = 2)     #Request same doctor again
        yield doctor_request2
        t_doc2 = env.now
        qstats.print_event(patient_id, qstats.CAT2, qstats.DOCTOR_TREAT, choice, t_doc2)

        yield env.timeout(treatment_time)
        t_doc2_end = env.now
        doctors[choice].release(doctor_request2)
        qstats.print_event(patient_id, qstats.CAT2, qstats.DOCTOR_TREAT_END, choice, t_doc2_end)

        bed.release(bed_request)
        
        timestamps = [t_arrive, t_triage, t_triage_end, t_bed, t_doc1,\
                      t_doc1_end, t_obs_end, t_doc2, t_doc2_end]
        qstats.notify_event(qstats.CAT2, timestamps)
        qstats.validate_event(CurrentPatient, qstats.CAT2, timestamps)

def CAT3(env, patient_id, triage_time, consultation_time, observe_time, treatment_time, doctors, nurses, bed, waiting_room_max, qstats):

    qstats.patient_num()
    CurrentPatient = qstats.CurrentPatient
    
    t_arrive = env.now
    qstats.print_event(patient_id, qstats.CAT3, qstats.ARRIVE, 0, t_arrive)
    
    triage_request = nurses.request()   #Patient sees triage nurse
    yield triage_request
    t_triage = env.now
    env.timeout(triage_time)
    nurses.release(triage_request)
    t_triage_end = env.now

    if len(bed.queue) == (waiting_room_max):   #Check to see if waiting room is full
        timestamps = [t_arrive, t_triage_end]
        qstats.notify_event(qstats.DIVERTED, timestamps)
        qstats.print_event(patient_id, qstats.CAT3, qstats.DIVERTED, 0, 0)
    
    else:
        bed_request = bed.request(priority = 3)     #Patient waits for a bed
        yield bed_request
        t_bed = env.now
        qstats.print_event(patient_id, qstats.CAT3, qstats.BED, 0, t_bed)

        doc_req = []    #Queue for all doctors, cancel all except the first 
        for i in range(len(doctors)):
            doc_req.append(doctors[i].request(priority = 5))

        doc_chosen = yield env.any_of(doc_req)

        doc_list = list(doc_chosen.keys())
        first_doc = doc_list[0]

        for j in range(len(doc_req)):
            if first_doc == doc_req[j]:
                choice = j
                for k in range(len(doc_req)):
                    if k != j:
                        if doc_req[k] in doc_list:
                            doctors[k].release(doc_req[k])
                        else:
                            doc_req[k].cancel()
                break

        t_doc1 = env.now
        qstats.print_event(patient_id, qstats.CAT3, qstats.DOCTOR, choice, t_doc1)

        yield env.timeout(consultation_time)    #Consultation time
        t_doc1_end = env.now
        qstats.print_event(patient_id, qstats.CAT3, qstats.DOCTOR_END, choice, t_doc1_end)

        doctors[choice].release(doc_req[choice])

        yield env.timeout(observe_time)     #Observation time
        t_obs_end = env.now
        qstats.print_event(patient_id, qstats.CAT3, qstats.OBS_END, choice, t_obs_end)

        doctor_request2 = doctors[choice].request(priority = 3)     #Request same doctor again
        yield doctor_request2
        t_doc2 = env.now
        qstats.print_event(patient_id, qstats.CAT3, qstats.DOCTOR_TREAT, choice, t_doc2)

        yield env.timeout(treatment_time)
        t_doc2_end = env.now
        doctors[choice].release(doctor_request2)
        qstats.print_event(patient_id, qstats.CAT3, qstats.DOCTOR_TREAT_END, choice, t_doc2_end)
        
        bed.release(bed_request)

        timestamps = [t_arrive, t_triage, t_triage_end, t_bed, t_doc1,\
                      t_doc1_end, t_obs_end, t_doc2, t_doc2_end]
        qstats.notify_event(qstats.CAT3, timestamps)
        qstats.validate_event(CurrentPatient, qstats.CAT3, timestamps)

#Simulation data and settings
#New arrival rates

CAT1_arrival_rate = 0.02    #patients / minute
CAT2_arrival_rate = 0.08    #patients / minute
CAT3_arrival_rate = 0.11    #patients / minute

#Old arrival rates
"""
CAT1_arrival_rate = 1 / 120    #patients / minute
CAT2_arrival_rate = 2 / 60  #patients / minute
CAT3_arrival_rate = 3 / 60   #patients / minute
"""

#Parameters
num_nurses = 3
num_doctors = 10
num_beds = 33
num_resus_rooms = 5
waiting_room_max = 20

#Time Parameters
triage_params = [3, 3.5, 4]
resus_params = [35, 60, 130]
consult_params = [5, 20, 20]
observe_params = [15, 40, 180]
treat_params = [8, 20, 30]

sim_end = 500
show_full_output = True
show_validation_output = False
save_to_csv = False
num_reps = 1

def simulation_run():
    #setup and run simulation
    qstats = Qstats(show_full_output, show_validation_output)
    env = sm.Environment()

    nurses = sm.Resource(env, num_nurses)
    beds = sm.PriorityResource(env, num_beds)
    resus_rooms = sm.Resource(env, num_resus_rooms)

    doctors = []
    for i in range(1,num_doctors+1):
        doctors.append(sm.PriorityResource(env, 1))

    env.process(arrivals(env, 1, CAT1_arrival_rate, triage_params, resus_params,\
                         consult_params, observe_params, treat_params, doctors,\
                         resus_rooms, nurses, beds, waiting_room_max, qstats))
    env.process(arrivals(env, 2, CAT2_arrival_rate, triage_params, resus_params,\
                         consult_params, observe_params, treat_params, doctors,\
                         resus_rooms, nurses, beds, waiting_room_max, qstats))
    env.process(arrivals(env, 3, CAT3_arrival_rate, triage_params, resus_params,\
                         consult_params, observe_params, treat_params, doctors,\
                         resus_rooms, nurses, beds, waiting_room_max, qstats))

    env.run(until = sim_end)

    #summary statistics
    qstats.display_summary_stats(sim_end, num_resus_rooms, num_doctors, num_beds, waiting_room_max)
    
    return qstats

def simulation_reps(num_reps):
    if save_to_csv:
        repf = open('sim_reps.csv', 'w')
        repf.write(str('CAT1_stay, CAT2_stay, CAT3_stay, Div_patients, CAT1_wait \n'))
    for rep in range(num_reps):
        print('******** REP', rep + 1, 'of', num_reps, '***********')
        qstats = simulation_run()
        if save_to_csv:
            repf.write(str(qstats.CAT1_stay_time_tot / qstats.CAT1dis)+', ')
            repf.write(str(qstats.CAT2_stay_time_tot / qstats.CAT2dis)+', ')
            repf.write(str(qstats.CAT3_stay_time_tot / qstats.CAT3dis)+', ')
            repf.write(str(qstats.patients_diverted / (qstats.dis_tot + qstats.patients_diverted) * 100)+', ')
            repf.write(str( (qstats.doc_wait_resus_tot + qstats.resus_wait_tot) / qstats.CAT1dis)+'\n')
    if save_to_csv:
        repf.close()

simulation_reps(num_reps)
