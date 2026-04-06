import streamlit as st
import pandas as pd

# הגדרות דף
st.set_page_config(page_title="מערכת ניהול תורמים - והשיב", layout="wide", initial_sidebar_state="collapsed")

# --- עיצוב CSS "נדרים פלוס" מקסימלי ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    
    /* סרגל עליון כהה */
    .top-nav { background-color: #3b566e; color: white; padding: 10px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #00b5ad; }
    
    /* סרגל אייקונים */
    .icon-bar { background-color: #5591ab; padding: 15px; display: flex; justify-content: center; gap: 25px; margin-bottom: 20px; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px; }
    .icon-item { color: white; text-align: center; font-size: 12px; cursor: pointer; }
    .icon-circle { background-color: white; color: #5591ab; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-size: 20px; }
    .icon-circle.active { background-color: #00b5ad; color: white; }

    /* עיצוב הטבלה */
    .nedarim-table-header { background-color: #00b5ad; color: white; padding: 10px; font-weight: bold; display: flex; border-radius: 5px 5px 0 0; }
    .table-row { border-bottom: 1px solid #ddd; padding: 10px; display: flex; align-items: center; background-color: white; transition: 0.2s; }
    .table-row:hover { background-color: #f1fafa; }
    
    /* כרטיס תורם (Modal-ish) */
    .donor-modal { background-color: white; border: 1px solid #ccc; border-radius: 15px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin-top: -20px; }
    .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px; }
    .close-btn { background-color: #ff7675; color: white; border-radius: 50%; width: 30px; height: 30px; text-align: center; line-height: 30px; cursor: pointer; }
    
    .field-label { color: #666; font-size: 13px; margin-bottom: 2px; }
    .field-value { border: 1px solid #eee; padding: 5px 10px; background: #fafafa; border-radius: 4px; margin-bottom: 10px; min-height: 30px; }

    /* כפתורים */
    .stButton>button { background-color: white; color: #00b5ad; border: 1px solid #00b5ad; border-radius: 5px; font-size: 14px; }
    .stButton>button:hover { background-color: #00b5ad; color: white; }
    </style>
    """, unsafe_allow_html=True)

# פונקציות עזר
def clean_currency(value):
    if pd.isna(value) or str(value).strip() in ["", "nan"]: return 0
    try:
        s = str(value).replace('₪', '').replace('$', '').replace(',', '').strip()
        return float(s.split()[0])
    except: return 0

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('donors.csv', encoding='utf-8-sig')
    except:
        df = pd.read_csv('donors.csv', encoding='cp1255')
    df.columns = [c.strip() for c in df.columns]
    return df

# --- אתחול נתונים ---
if 'view' not in st.session_state: st.session_state.view = 'list'
if 'selected_donor_idx' not in st.session_state: st.session_state.selected_donor_idx = None

# טעינת דאטה
df = load_data()
personal_cols = ['משפחה', 'פרטי', 'רחוב', 'טלפון', 'טלפון נוסף', 'קהילה']
campaign_cols = [c for c in df.columns if c not in personal_cols and "Full_Name" not in c]

# --- מבנה הדף העליון ---
st.markdown("""
    <div class="top-nav">
        <div>והשיב - ארגון להורים לנוער מתמודד - א.ח</div>
        <div style="font-size:12px;">מחובר כעת: שלמה סופר</div>
    </div>
    <div class="icon-bar">
        <div class="icon-item"><div class="icon-circle">🏠</div>דף הבית</div>
        <div class="icon-item"><div class="icon-circle">⚙️</div>הגדרות</div>
        <div class="icon-item"><div class="icon-circle">💳</div>אשראי</div>
        <div class="icon-item"><div class="icon-circle active">👥</div>ניהול תורמים</div>
        <div class="icon-item"><div class="icon-circle">🏦</div>בנקאי</div>
        <div class="icon-item"><div class="icon-circle">📊</div>דוחות</div>
    </div>
""", unsafe_allow_html=True)

# --- לוגיקת תצוגה ---

# 1. תצוגת רשימה (הטבלה הראשית)
if st.session_state.view == 'list':
    st.markdown("<h3 style='text-align:center;'>מערכת ניהול תורמים</h3>", unsafe_allow_html=True)
    
    # כפתורי פעולה עליונים
    c1, c2, c3, c4, c5 = st.columns([1,1,1,1,2])
    c1.button("➕ הוספת תורם")
    c2.button("🔄 רענון נתונים")
    search_term = c5.text_input("🔍 חיפוש תורם:", placeholder="הקלד שם או טלפון...")

    # כותרת הטבלה בטורקיז
    st.markdown("""
        <div class="nedarim-table-header">
            <div style="flex:1">זהות</div>
            <div style="flex:3">שם</div>
            <div style="flex:3">כתובת</div>
            <div style="flex:2">טלפונים</div>
            <div style="flex:0.5">ערוך</div>
        </div>
    """, unsafe_allow_html=True)

    # סינון וחיפוש
    filtered_df = df
    if search_term:
        filtered_df = df[df['משפחה'].str.contains(search_term, na=False) | df['פרטי'].str.contains(search_term, na=False)]

    for idx, row in filtered_df.iterrows():
        cols = st.columns([1, 3, 3, 2, 0.5])
        cols[0].write(f"{idx+1000}")
        cols[1].write(f"**{row['משפחה']} {row['פרטי']}**")
        cols[2].write(row['רחוב'])
        cols[3].write(row['טלפון'])
        if cols[4].button("✏️", key=f"edit_{idx}"):
            st.session_state.selected_donor_idx = idx
            st.session_state.view = 'card'
            st.rerun()

# 2. תצוגת כרטיס תורם (ה-Popup)
elif st.session_state.view == 'card':
    idx = st.session_state.selected_donor_idx
    row = df.loc[idx]
    
    # כפתור סגירה (X)
    if st.button("✖️ סגור וחזור לרשימה"):
        st.session_state.view = 'list'
        st.rerun()

    st.markdown('<div class="donor-modal">', unsafe_allow_html=True)
    st.subheader(f"📄 כרטיס תורם: {row['משפחה']} {row['פרטי']}")
    
    # חלוקה ל-2 טורים כמו בצילום מסך
    top_c1, top_c2 = st.columns(2)
    
    with top_c1: # צד ימין - פרטי זהות
        st.markdown('<p class="field-label">שם משפחה:</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row["משפחה"]}</div>', unsafe_allow_html=True)
        st.markdown('<p class="field-label">שם פרטי:</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row["פרטי"]}</div>', unsafe_allow_html=True)
        st.markdown('<p class="field-label">כתובת:</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row["רחוב"]}</div>', unsafe_allow_html=True)

    with top_c2: # צד שמאל - תקשורת
        st.markdown('<p class="field-label">טלפון 1:</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row["טלפון"]}</div>', unsafe_allow_html=True)
        st.markdown('<p class="field-label">טלפון נוסף:</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row["טלפון נוסף"]}</div>', unsafe_allow_html=True)
        st.markdown('<p class="field-label">קהילה:</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="field-value">{row["קהילה"]}</div>', unsafe_allow_html=True)

    # היסטוריית עסקאות (הטבלה למטה)
    st.markdown("---")
    st.markdown("<h4>📋 היסטוריית תרומות (מכלול)</h4>", unsafe_allow_html=True)
    
    history_data = []
    total_all_time = 0
    for col in campaign_cols:
        val = row[col]
        num_val = clean_currency(val)
        if num_val > 0:
            history_data.append({"קמפיין": col, "סכום": val, "תאריך/שנה": col.split()[-1]})
            total_all_time += num_val

    if history_data:
        st.table(pd.DataFrame(history_data))
        st.markdown(f"<h3 style='color:#00b5ad; text-align:left;'>סה''כ מכלול: ₪{total_all_time:,.0f}</h3>", unsafe_allow_html=True)
    else:
        st.info("אין היסטוריית תרומות לתורם זה.")
    
    st.markdown('</div>', unsafe_allow_html=True)
