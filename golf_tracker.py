import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# --- 設定網頁標題與寬度 ---
st.set_page_config(page_title="高爾夫戰績與行程紀錄", layout="centered")

# --- 定義資料儲存路徑 (單機 JSON 檔案) ---
DATA_FILE_SCORE = "golf_scores.json"
DATA_FILE_FINANCE = "golf_finance.json"
DATA_FILE_SCHEDULE = "golf_schedule.json"

# --- 輔助函數：讀取與儲存資料 ---
def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 載入現有資料 ---
scores_data = load_data(DATA_FILE_SCORE)
finance_data = load_data(DATA_FILE_FINANCE)
schedule_data = load_data(DATA_FILE_SCHEDULE)

# --- 側邊欄導覽 ---
st.sidebar.title("⛳ 高爾夫紀錄本")
page = st.sidebar.radio("請選擇功能：", ["📝 場上計分 (18洞)", "💰 財務與抓球結算", "📅 約球行程表", "📊 戰績總覽"])

# ==========================================
# 頁面 1：場上計分 (18洞快速輸入)
# ==========================================
if page == "📝 場上計分 (18洞)":
    st.header("📝 新增一場球局成績")
    
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("打球日期", datetime.today())
    with col2:
        # 改為自行輸入球場名稱
        course = st.text_input("輸入球場名稱")

    # 只要有輸入球場名稱，就顯示下方的 18 洞表單
    if course:
        st.write("---")
        st.subheader("⛳ 18 洞成績快速輸入")
        
        with st.form("score_form"):
            st.markdown("請注意：Par 3 的洞請勿勾選 FIR (上球道)。")
            
            hole_data = []
            for i in range(1, 19):
                st.markdown(f"**第 {i} 洞**")
                col_score, col_putt, col_fir, col_gir = st.columns([1, 1, 1, 1])
                
                with col_score:
                    score = st.number_input(f"總桿", min_value=1, max_value=20, value=4, key=f"score_{i}")
                with col_putt:
                    putt = st.number_input(f"推桿", min_value=0, max_value=10, value=2, key=f"putt_{i}")
                with col_fir:
                    fir = st.checkbox(f"FIR (上球道)", key=f"fir_{i}")
                with col_gir:
                    gir = st.checkbox(f"GIR (標上)", key=f"gir_{i}")
                
                hole_data.append({
                    "hole": i,
                    "score": score,
                    "putt": putt,
                    "fir": fir,
                    "gir": gir
                })
                st.write("") 

            submit_score = st.form_submit_button("💾 儲存這場球成績")
            
            if submit_score:
                total_score = sum([h['score'] for h in hole_data])
                total_putts = sum([h['putt'] for h in hole_data])
                total_fir = sum([1 for h in hole_data if h['fir']])
                total_gir = sum([1 for h in hole_data if h['gir']])
                
                new_record = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "date": str(date),
                    "course": course,
                    "total_score": total_score,
                    "total_putts": total_putts,
                    "total_fir": total_fir,
                    "total_gir": total_gir,
                    "details": hole_data
                }
                scores_data.append(new_record)
                save_data(scores_data, DATA_FILE_SCORE)
                st.success(f"✅ 成績已儲存！總桿：{total_score} 桿")

# ==========================================
# 頁面 2：財務與抓球結算
# ==========================================
elif page == "💰 財務與抓球結算":
    st.header("💰 財務紀錄 (球資與抓球)")
    
    with st.form("finance_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_fin = st.date_input("日期", datetime.today())
        with col2:
             course_fin = st.text_input("球場名稱 (選填)")

        st.write("---")
        st.subheader("💵 今日花費與輸贏")
        
        cost = st.number_input("今日球資總計 (果嶺+桿弟+球車+賣店等)", min_value=0, value=3500, step=100)
        
        st.markdown("抓球結算：贏錢請輸入正數，輸錢請輸入負數 (例如：-500)")
        bet_result = st.number_input("抓球總結算", value=0, step=100)
        
        notes = st.text_input("備註 (例如：今天跟誰打、誰贏最多)")
        
        submit_fin = st.form_submit_button("💾 儲存財務紀錄")
        
        if submit_fin:
             new_fin = {
                 "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                 "date": str(date_fin),
                 "course": course_fin,
                 "cost": cost,
                 "bet_result": bet_result,
                 "net_total": bet_result - cost, 
                 "notes": notes
             }
             finance_data.append(new_fin)
             save_data(finance_data, DATA_FILE_FINANCE)
             st.success("✅ 財務紀錄已儲存！")

# ==========================================
# 頁面 3：約球行程表
# ==========================================
elif page == "📅 約球行程表":
    st.header("📅 即將到來的球局")
    
    with st.form("schedule_form"):
        st.subheader("新增約球行程")
        col1, col2 = st.columns(2)
        with col1:
            sch_date = st.date_input("打球日期")
        with col2:
            sch_time = st.time_input("Tee Time (開球時間)")
            
        # 改為自行輸入預定球場
        sch_course = st.text_input("輸入預定球場")
        sch_players = st.text_input("同行球友 (請用逗號分隔)")
        
        submit_sch = st.form_submit_button("💾 新增行程")
        
        if submit_sch:
             if sch_course.strip() == "":
                 st.error("請輸入球場名稱！")
             else:
                 new_sch = {
                     "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                     "date": str(sch_date),
                     "time": str(sch_time),
                     "course": sch_course,
                     "players": sch_players
                 }
                 schedule_data.append(new_sch)
                 save_data(schedule_data, DATA_FILE_SCHEDULE)
                 st.success("✅ 行程已新增！")
             
    st.write("---")
    st.subheader("📋 目前行程列表")
    if schedule_data:
        df_sch = pd.DataFrame(schedule_data)
        df_sch = df_sch.sort_values(by="date")
        st.dataframe(df_sch[['date', 'time', 'course', 'players']], hide_index=True)
    else:
        st.info("目前沒有即將到來的行程。")

# ==========================================
# 頁面 4：戰績總覽
# ==========================================
elif page == "📊 戰績總覽":
    st.header("📊 歷史戰績與財務總覽")
    
    tab1, tab2 = st.tabs(["成績統計", "財務統計"])
    
    with tab1:
        if scores_data:
            df_scores = pd.DataFrame(scores_data)
            st.dataframe(df_scores[['date', 'course', 'total_score', 'total_putts', 'total_fir', 'total_gir']], hide_index=True)
            
            st.subheader("📈 表現趨勢")
            st.line_chart(df_scores.set_index('date')['total_score'])
            
            avg_score = df_scores['total_score'].mean()
            st.metric("平均總桿", f"{avg_score:.1f} 桿")
        else:
            st.info("尚無成績紀錄。")

    with tab2:
        if finance_data:
            df_fin = pd.DataFrame(finance_data)
            st.dataframe(df_fin[['date', 'course', 'cost', 'bet_result', 'notes']], hide_index=True)
            
            total_cost = df_fin['cost'].sum()
            total_bet = df_fin['bet_result'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("歷史總球資花費", f"-${total_cost:,}")
            col2.metric("抓球總輸贏", f"${total_bet:,}")
        else:
             st.info("尚無財務紀錄。")