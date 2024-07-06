import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_BASE_URL = os.getenv("API_URL")

def get_specialties():
    response = requests.get(f"{API_BASE_URL}/specialties")
    return response.json()

def get_doctors():
    response = requests.get(f"{API_BASE_URL}/doctors")
    return response.json()

def get_available_schedules(specialty, crm=None):
    params = {"crm": crm} if crm else {}
    response = requests.get(f"{API_BASE_URL}/available_schedules/{specialty}", params=params)
    return response.json()

def register_patient(name, phone):
    data = {"name": name, "phone": phone}
    response = requests.post(f"{API_BASE_URL}/patients", json=data)
    return response.status_code == 200

def schedule_appointment(patient_id, doctor_id, date, time):
    data = {"patient_id": patient_id, "doctor_id": doctor_id, "date": date, "time": time}
    response = requests.post(f"{API_BASE_URL}/appointments", json=data)
    return response.status_code == 200

def get_patients():
    response = requests.get(f"{API_BASE_URL}/patients")
    return response.json()

def register_arrival(appointment_id):
    response = requests.patch(f"{API_BASE_URL}/appointments/{appointment_id}", json={"arrived": True})
    return response.status_code == 200

def register_consultation_details(appointment_id, diagnosis, amount_paid, payment_method):
    data = {
        "diagnosis": diagnosis,
        "amount_paid": amount_paid,
        "payment_method": payment_method
    }
    response = requests.patch(f"{API_BASE_URL}/appointments/{appointment_id}", json=data)
    return response.status_code == 200

st.set_page_config(layout="wide")

st.title('CLIMED')
st.subheader('Sistema de Gerenciamento de Consultas Médicas')

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Cadastro de Paciente", "Agendamento de Consulta", "Registro de Chegada", "Visualização de Agenda", "Detalhes da Consulta", "Lista de Pacientes"])

with tab1:
    st.header("Cadastro de Paciente")
    name = st.text_input("Nome do Paciente")
    phone = st.text_input("Telefone")
    if st.button("Registrar Paciente"):
        if register_patient(name, phone):
            st.success("Paciente registrado com sucesso.")
        else:
            st.error("Falha ao registrar paciente.")

with tab2:
    st.header("Agendamento de Consulta")
    patient_name = st.text_input("Nome do Paciente para Busca")
    specialty = st.selectbox("Especialidade Médica", get_specialties())
    doctor_name = st.text_input("Nome do Médico (opcional)")
    doctors = get_doctors()
    doctor_id = st.selectbox("Selecione o Médico", [m['name'] for m in doctors])
    schedules = get_available_schedules(specialty)
    time_slot = st.selectbox("Horários Disponíveis", [f"{a['start_time']} - {a['end_time']}" for a in schedules])
    if st.button("Agendar Consulta"):
        if schedule_appointment(patient_name, doctor_id, date, time):
            st.success("Consulta agendada com sucesso.")
        else:
            st.error("Falha ao agendar consulta.")

with tab3:
    st.header("Registro de Chegada")
    schedules = get_available_schedules()
    for schedule in schedules:
        st.subheader(f"Paciente: {schedule['patient_name']} - {schedule['start_time']}")
        if st.button(f"Confirmar Chegada de {schedule['patient_name']}"):
            if register_arrival(schedule['appointment_id']):
                st.success("Chegada confirmada!")
            else:
                st.error("Falha ao confirmar chegada.")

with tab4:
    st.header("Visualização de Agenda")
    doctors = get_doctors()
    doctor_id = st.selectbox("Selecione o Médico", [m['name'] for m in doctors])
    doctor_schedule = get_available_schedules(doctor_id)
    for appointment in doctor_schedule:
        st.write(f"{appointment['start_time']} - {appointment['end_time']}: {appointment['patient_name']}")

with tab5:
    st.header("Detalhes da Consulta")
    appointments = get_available_schedules()
    appointment_id = st.selectbox("Selecione Consulta", [c['id'] for c in appointments])
    consultation_details = appointments[appointment_id]
    st.write(f"Paciente: {consultation_details['patient_name']}")

    diagnosis = st.text_area("Diagnóstico")
    payment = st.number_input("Valor Pago", min_value=0.0, format='%.2f')
    payment_method = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "Boleto"])

    if st.button("Registrar Detalhes"):
        if register_consultation_details(appointment_id, diagnosis, payment, payment_method):
            st.success("Detalhes registrados com sucesso!")
        else:
            st.error("Falha ao registrar detalhes da consulta.")

with tab6:
    st.header("Lista de Pacientes")
    patients = get_patients()
    for patient in patients:
        st.write(f"{patient['name']} - {patient['phone']}")
