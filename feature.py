import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import base64
import pandas as pd
import google.generativeai as genai

genai.configure(api_key='AIzaSyB3F-YSBR2-ZbBvJUodyIuxo4DTVJ43KoU')
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_cv(job_data, candidate_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, f"CV for {job_data['job_title']} at {job_data['company_name']}")

    # Job Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 90, "Job Details:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 110, f"Company Name: {job_data['company_name']}")
    c.drawString(50, height - 130, f"Address: {job_data['company_address']}")
    c.drawString(50, height - 150, f"Field: {job_data['company_field']}")
    c.drawString(50, height - 170, f"Scale: {job_data['company_size']}")
    c.drawString(50, height - 190, f"Nationality: {job_data['company_nationality']}")
    c.drawString(50, height - 210, f"Experience Required: {job_data['experience_required']} years")
    c.drawString(50, height - 230, f"Level: {job_data['job_level']}")
    c.drawString(50, height - 250, f"Type: {job_data['job_type']}")
    c.drawString(50, height - 270, f"Contract Type: {job_data['contract_type']}")
    c.drawString(50, height - 290, f"Technology Requirements: {', '.join(job_data['technology_requirements'])}")
    c.drawString(50, height - 310, f"Interview Process: {job_data['interview_process']}")
    c.drawString(50, height - 330, f"Job Description: {job_data['job_description']}")
    c.drawString(50, height - 350, f"Company Information: {job_data['company_info']}")

    # Candidate Information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 380, "Candidate Details:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 400, f"Name: {candidate_data['name']}")
    c.drawString(50, height - 420, f"Email: {candidate_data['email']}")
    c.drawString(50, height - 440, f"Phone: {candidate_data['phone']}")
    c.drawString(50, height - 460, f"Skills: {', '.join(candidate_data['skills'])}")

    c.save()
    buffer.seek(0)
    return buffer

def embed_pdf(pdf_data):
    base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="750" height="1200" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def tab_4():
    st.header("Feature")
    # Path to the CSV file
    csv_file_path = "processed_data.csv"  # Replace with your file path

    # Load the CSV file
    df = pd.read_csv(csv_file_path)

    df['quy_mo_cong_ty'] = df['quy_mo_cong_ty'].apply(lambda x: f"Quy mô {x}")
    df['nam_kinh_nghiem'] = df['nam_kinh_nghiem'].apply(lambda x: f"{int(x)} năm kinh nghiệm")

    def extract_city_province(address): 
        parts = address.strip("[]'").split(',') 
        return ', '.join([part.strip() for part in parts[-2:]])
    df['dia_chi'] = df['dia_chi'].apply(extract_city_province)

    def convert_string(s): 
        return s.strip("[]'").replace("', '", ", ")
    df['nganh_nghe'] = df['nganh_nghe'].apply(convert_string)
    df['quoc_tich_cong_ty'] = df['quoc_tich_cong_ty'].apply(convert_string)
    df['cap_bac'] = df['cap_bac'].apply(convert_string)
    df['loai_hinh'] = df['loai_hinh'].apply(convert_string)
    df['loai_hop_dong'] = df['loai_hop_dong'].apply(convert_string)
    df['cong_nghe_su_dung'] = df['cong_nghe_su_dung'].apply(convert_string)
    df['quy_trinh_phong_van'] = df['quy_trinh_phong_van'].apply(convert_string)
    df['nhom_cong_viec'] = df["nhom_cong_viec"].apply(convert_string)
    
    data = df.copy()
    
    data.columns = ["Tên công việc",
                "Tên công ty",
                "Mức lương",
                "Địa chỉ",
                "Ngày đăng",
                "Ngành nghề",
                "Quy mô công ty",
                "Quốc tịch công ty",
                "Số năm kinh nghiệm",
                "Cấp bậc",
                "Loại hình",
                "Loại hợp đồng",
                "Công nghệ sử dụng",
                "Quy trình phỏng vấn",
                "Mô tả công việc",
                "Thông tin công ty",
                "URL",
                "Thời gian hiện tại",
                "URL công ty",
                "Số lượng nhân viên",
                "Nhóm công việc"]
    
    data["Mức lương"] = data["Mức lương"].apply(lambda x: "Thương lượng" if x=="[0, 0]" else x)
    
    # Display the dataframe
    st.dataframe(data)

    # Select a row by showing the index
    row_to_select = st.selectbox("Select a row:", df.index)

    # Split into two columns
    col1, col2 = st.columns(2)

    # Job Details Input
    with col1:
        st.write("### Job Details")
        job_title = st.text_input("Job Title", str(df.ten_cong_viec[row_to_select]))
        company_name = st.text_input("Company Name", str(df.ten_cong_ty[row_to_select]))
        company_address = st.text_input("Company Address", str(df.dia_chi[row_to_select]))
        company_field = st.text_input("Field", str(df.nganh_nghe[row_to_select]))
        company_size = st.text_input("Company Size", str(df.quy_mo_cong_ty[row_to_select]))
        company_nationality = st.text_input("Nationality", str(df.quoc_tich_cong_ty[row_to_select]))
        job_level = st.text_input("Level", str(df.cap_bac[row_to_select]))
        job_type = st.text_input("Job Type", str(df.loai_hinh[row_to_select]))
        contract_type = st.text_input("Contract Type", str(df.loai_hop_dong[row_to_select]))
        # experience_required = st.text_input("Experience Required (years)", min_value=0.0, max_value=10.0, value=float(df.nam_kinh_nghiem[row_to_select]), step=0.5)
        experience_required = st.text_input("Experience Required (years)", str(df.nam_kinh_nghiem[row_to_select]))
        technology_requirements = st.text_area("Technology Requirements (comma-separated)", str(df.cong_nghe_su_dung[row_to_select]))
        interview_process = st.text_area("Interview Process", str(df.quy_trinh_phong_van[row_to_select]))
        job_description = st.text_area("Job Description", str(df.mo_ta_cong_viec[row_to_select]))
        company_info = st.text_area("Company Information", str(df.thong_tin_cong_ty[row_to_select]))

    # Candidate Details Input
    with col2:
        st.write("### Candidate Details")
        # name = st.text_input("Candidate Name", "John Doe")
        # email = st.text_input("Candidate Email", "john.doe@example.com")
        # phone = st.text_input("Candidate Phone", "+123456789")
        # skills = st.text_area("Candidate Skills (comma-separated)", "Python, Data Analysis, Team Leadership").split(',')
        describe = st.text_area("Describe Yourself")

    # Predict salary
    with col1:
        if st.button("Predict Salary ($)"):
            prompt = f""" Cho thông tin của một công việc như sau:

            1. Tên công việc: {job_title}
            2. Tên công ty: {company_name}
            3. Địa chỉ: {company_address}
            4. Lĩnh vực của công ty: {company_field}
            5. Quy mô công ty: {company_size}
            6. Quốc tịch công ty: {company_nationality}
            7. Yêu cầu về số năm kinh nghiệm: {experience_required}
            8. Cấp bậc: {job_level}
            9. Loại hình: {job_type}
            10. Loại hợp đồng: {contract_type}
            11. Yêu cầu về công nghệ: {technology_requirements}
            12. Quy trình phỏng vấn: {interview_process}
            13. Mô tả công việc: {job_description}
            14. Thông tin công ty: {company_info}

            Hãy dự đoán khoảng của mức lương theo đơn vị USD, chỉ trả lời giá trị số theo cú pháp:
            "<Giá trị nhỏ nhất> - <Giá trị lớn nhất>"
            """

            markdown_string = model.generate_content(prompt).text
            st.markdown(markdown_string)

    # Generate CV
    with col2:
        # if st.button("Generate CV PDF"):
        if st.button("Get Advice"):
            job_data = {
                "job_title": job_title,
                "company_name": company_name,
                "company_address": company_address,
                "company_field": company_field,
                "company_size": company_size,
                "company_nationality": company_nationality,
                "experience_required": experience_required,
                "job_level": job_level,
                "job_type": job_type,
                "contract_type": contract_type,
                "technology_requirements": [tech.strip() for tech in technology_requirements],
                "interview_process": interview_process,
                "job_description": job_description,
                "company_info": company_info,
            }

            candidate_data = {
                # "name": name,
                # "email": email,
                # "phone": phone,
                # "skills": [skill.strip() for skill in skills],
                "describe": describe,
            }

            prompt = f""" Cho thông tin của một công việc như sau:

            1. Tên công việc: {job_title}
            2. Tên công ty: {company_name}
            3. Địa chỉ: {company_address}
            4. Lĩnh vực của công ty: {company_field}
            5. Quy mô công ty: {company_size}
            6. Quốc tịch công ty: {company_nationality}
            7. Yêu cầu về số năm kinh nghiệm: {experience_required}
            8. Cấp bậc: {job_level}
            9. Loại hình: {job_type}
            10. Loại hợp đồng: {contract_type}
            11. Yêu cầu về công nghệ: {technology_requirements}
            12. Quy trình phỏng vấn: {interview_process}
            13. Mô tả công việc: {job_description}
            14. Thông tin công ty: {company_info}

            Và thông tin của ứng viên như sau:
            {describe}

            Xem xét khả năng đậu công việc của ứng viên dựa vào thông tin đã cho.
            Đưa ra lời khuyên cho ứng viên.
            """

            markdown_string = model.generate_content(prompt).text
            st.markdown(markdown_string)

            # pdf_buffer = generate_cv(job_data, candidate_data)
            # pdf_data = pdf_buffer.getvalue()

            # st.write("### CV PDF Preview")
            # embed_pdf(pdf_data)

            # st.download_button(
            #     label="Download CV",
            #     data=pdf_data,
            #     file_name="cv_based_on_job.pdf",
            #     mime="application/pdf"
            # )  