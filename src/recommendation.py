import pandas as pd
import streamlit as st

df = pd.read_csv('processed_data.csv')

col = ['ten_cong_viec', 'ten_cong_ty', 'muc_luong', 'dia_chi', 'nganh_nghe', 'quy_mo_cong_ty', 'quoc_tich_cong_ty',
       'nam_kinh_nghiem', 'cap_bac', 'loai_hinh', 'loai_hop_dong', 'cong_nghe_su_dung', 'url', 'url_cong_ty']
df = df[col]

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

# df['url'] = df['url'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')

# Trọng số cho từng features
weights = {
    'ten_cong_viec': 10,
    'ten_cong_ty': 5,
    'muc_luong': 5,
    'dia_chi': 10,
    'nganh_nghe': 8,
    'quy_mo_cong_ty': 2,
    'quoc_tich_cong_ty': 5,
    'nam_kinh_nghiem': 8,
    'cap_bac': 8,
    'loai_hinh': 5,
    'loai_hop_dong': 5,
    'cong_nghe_su_dung': 10,
}

total_weight = sum(weights.values())
weights = {key: value / total_weight for key, value in weights.items()}

df = df.drop_duplicates()

def tab_2():
    st.header("Recommendation")
    # Khởi tạo biến trong session_state nếu chưa có
    if 'input_count' not in st.session_state:
        st.session_state.input_count = 1

    if 'inputs' not in st.session_state:
        st.session_state.inputs = [""]

    def add_input():
        st.session_state.input_count += 1

    def reload():
        st.session_state.input_count = 0
        st.session_state.inputs = [""]

    st.button('Tạo mới', on_click=reload) 

    # Tạo các ô input hiện tại
    for i in range(st.session_state.input_count):
        input_value = st.text_input(f'Từ khóa {i+1}:', key=f'input_{i}') 
        if input_value:
            # Cập nhật giá trị input vào session_state
            if len(st.session_state.inputs) < st.session_state.input_count:
                st.session_state.inputs.append(input_value)
            else:
                st.session_state.inputs[i] = input_value


    st.button('Thêm từ khóa', on_click=add_input)    

    # Các từ khóa cần tìm
    keywords = st.session_state.inputs

    # Hàm kiểm tra sự hiện diện của tất cả các từ khóa trong một dòng
    def contains_all_keywords(row, keywords):
        cols_to_consider = col[:-2]
        return all(any(keyword.lower() in str(row[col]).lower() for col in cols_to_consider) for keyword in keywords)

    # Lọc các dòng có tất cả các từ khóa
    filtered_df = df[df.apply(lambda row: contains_all_keywords(row, keywords), axis=1)]

    # Hàm tính tỷ lệ khớp từ khóa tự do với trọng số thuộc tính
    def weighted_match_probability(row, keywords, weights):
        match_score = 0
        max_score = sum(weights.values())
        cols_to_consider = col[:-2]
        for attribute, weight in weights.items():
            if any(keyword.lower() in str(row[attribute]).lower() for keyword in keywords):
                match_score += weight
        return match_score / max_score

    # Tính tỷ lệ khớp cho các dòng đã lọc
    filtered_df['Tỷ lệ khớp'] = filtered_df.apply(lambda row: weighted_match_probability(row, keywords, weights), axis=1)

    # Sắp xếp theo tỷ lệ khớp giảm dần
    sorted_df = filtered_df.sort_values(by='Tỷ lệ khớp', ascending=False)

    col1, col2, col3 = st.columns([3, 2, 15])
    with col1:
        st.write("Số công việc muốn hiển thị:")
    with col2:
        st.write(""" 
                <style> div[data-testid="stNumberInput"] > label { display: none; } 
                div[data-testid="stNumberInput"] > div { margin-top: -23px; } 
                </style> 
                """, 
                unsafe_allow_html=True) 
        num_rows = st.number_input("", min_value=1, max_value=len(df), value=5)


    # Hiển thị các tin tuyển dụng sắp xếp theo tỷ lệ khớp
    if st.button('Bắt đầu tìm kiếm công việc'): 
        if st.session_state.inputs != []: 
            if len(sorted_df) > 0:
                print(sorted_df.columns)
                data = sorted_df.copy()
                data.columns = ["Tên công việc",
                              "Tên công ty",
                              "Mức lương",
                              "Địa chỉ",
                            #   "Ngày đăng",
                              "Ngành nghề",
                              "Quy mô công ty",
                              "Quốc tịch công ty",
                              "Số năm kinh nghiệm",
                              "Cấp bậc",
                              "Loại hình",
                              "Loại hợp đồng",
                              "Công nghệ sử dụng",
                            #   "Quy trình phỏng vấn",
                            #   "Mô tả công việc",
                            #   "Thông tin công ty",
                              "URL",
                            #   "Thời gian hiện tại",
                              "URL công ty",
                              "Tỷ lệ khớp"]
                data["Mức lương"] = data["Mức lương"].apply(lambda x: "Thương lượng" if x=="[0, 0]" else x)
                st.write(data.head(num_rows))
            else:
                st.write('Hiện tại không có công việc phù hợp.')
        else: 
            st.write('Hãy nhập ít nhất một từ khóa để tìm kiếm công việc.')


