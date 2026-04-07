import streamlit as st
import pandas as pd
import os

# 1. הגדרות דף ועיצוב נדרים פלוס
st.set_page_config(page_title="יד תומך - ניהול תורמים", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    
    .top-nav { background-color: #3b566e; color: white; padding: 10px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 4px solid #00b5ad; }
    .icon-bar { background-color: #5591ab; padding: 15px; display: flex; justify-content: center; gap: 30px; margin-bottom: 20px; border-radius: 0 0 20px 20px; }
    .icon-item { color: white; text-align: center; font-size: 13px; }
    .icon-circle { background-color: white; color: #5591ab; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-size: 22px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
    .active-icon { background-color: #00b5ad !important; color: white !important; }

    .nedarim-header { background-color: #00b5ad; color: white; padding: 12px; font-weight: bold; display: flex; border-radius: 8px 8px 0 0; }
    .donor-card { background-color: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); border-right: 12px solid #00b5ad; }
    .field-box { background: #f8fbfc; border: 1px solid #e1e8eb; padding: 8px 12px; border-radius: 5px; margin-bottom: 12px; min-height: 40px; }
    .field-label { font-size: 13px; color: #666; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. פונקציות לוגיקה
def clean_money(val):
    if pd.isna(val) or str(val).strip() in ["", "nan", "0"]: return 0.0
    try:
        res = str(val).replace('₪','').replace('$','').replace(',','').strip().split()[0]
        return float(res)
    except: return 0.0

@st.cache_data
def load_data():
    try:
        df = pd.read_csv('donors.csv', encoding='utf-8-sig')
    except:
        df = pd.read_csv('donors.csv', encoding='cp1255')
    
    df.columns = [c.strip() for c in df.columns]
    
    # חישוב "מכלול" בצורה בטוחה (תיקון השגיאה שהופיעה)
    personal = ['משפחה', 'פרטי', 'רחוב', 'טלפון', 'טלפון נוסף', 'קהילה', 'אשראי']
    hags = [c for c in df.columns if c not in personal]
    
    # שימוש ב-apply במקום applymap למניעת שגיאת AttributeError
    df['מכלול'] = df[hags].apply(lambda col: col.map(clean_money)).sum(axis=1)
    return df, hags

# --- טעינת נתונים ---
df, campaign_cols = load_data()

# --- ניהול דפים ---
if 'page' not in st.session_state: st.session_state.page = 'list'
if 'selected_idx' not in st.session_state: st.session_state.selected_idx = None

# --- סרגל עליון עם לוגו ---
col_logo_1, col_logo_2 = st.columns([1, 8])
with col_logo_1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=70)
with col_logo_2:
    st.markdown("""
        <div class="top-nav">
            <div style="font-size:22px; font-weight:bold;">יד תומך - ארגון להורים לנוער מתמודד</div>
            <div style="font-size:14px;">שלום, מנהל המערכת | יציאה</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="icon-bar">
        <div class="icon-item"><div class="icon-circle">🏠</div>דף הבית</div>
        <div class="icon-item"><div class="icon-circle">📊</div>דוחות</div>
        <div class="icon-item"><div class="icon-circle active-icon">👥</div>ניהול תורמים</div>
        <div class="icon-item"><div class="icon-circle">💳</div>סליקה</div>
        <div class="icon-item"><div class="icon-circle">⚙️</div>הגדרות</div>
    </div>
""", unsafe_allow_html=True)

# 3. אבטחה
password = st.sidebar.text_input("סיסמת מערכת", type="password")
if password == "dudi330582008":

    # --- דף רשימה ---
    if st.session_state.page == 'list':
        st.subheader("🔍 חיפוש וניהול תורמים")
        search = st.text_input("", placeholder="חפש לפי שם, טלפון או כתובת...")
        
        st.markdown("""
            <div class="nedarim-header">
                <div style="flex:1.5">מכלול</div><div style="flex:3">שם התורם</div>
                <div style="flex:3">כתובת</div><div style="flex:2">טלפון</div><div style="flex:1">פעולה</div>
            </div>
        """, unsafe_allow_html=True)

        view_df = df
        if search:
            view_df = df[df.apply(lambda r: search in str(r.values), axis=1)]

        for i, row in view_df.iterrows():
            cols = st.columns([1.5, 3, 3, 2, 1])
            cols[0].write(f"**₪{row['מכלול']:,.0f}**")
            cols[1].write(f"{row['משפחה']} {row['פרטי']}")
            cols[2].write(row['רחוב'] if pd.notna(row['רחוב']) else "---")
            cols[3].write(row['טלפון'] if pd.notna(row['טלפון']) else "---")
            if cols[4].button("ערוך ✏️", key=f"edit_{i}"):
                st.session_state.selected_idx = i
                st.session_state.page = 'card'
                st.rerun()

    # --- דף כרטיס תורם ---
    elif st.session_state.page == 'card':
        idx = st.session_state.selected_idx
        donor = df.loc[idx]
        
        if st.button("⬅️ חזרה לרשימה"):
            st.session_state.page = 'list'
            st.rerun()

        st.markdown('<div class="donor-card">', unsafe_allow_html=True)
        st.title(f"📄 כרטיס תורם: {donor['משפחה']} {donor['פרטי']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<p class="field-label">שם משפחה:</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="field-box">{donor["משפחה"]}</div>', unsafe_allow_html=True)
            st.markdown('<p class="field-label">שם פרטי:</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="field-box">{donor["פרטי"]}</div>', unsafe_allow_html=True)
            st.markdown('<p class="field-label">כתובת:</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="field-box">{donor["רחוב"]}</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<p class="field-label">טלפון:</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="field-box">{donor["טלפון"]}</div>', unsafe_allow_html=True)
            st.markdown('<p class="field-label">טלפון נוסף:</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="field-box">{donor["טלפון נוסף"]}</div>', unsafe_allow_html=True)
            st.markdown('<p class="field-label">קהילה:</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="field-box">{donor["קהילה"]}</div>', unsafe_allow_html=True)

        # כפתור אשראי עם PIN
        st.write("")
        with st.popover("💳 צפייה בפרטי אשראי"):
            pin = st.text_input("הזן קוד PIN לצפייה:", type="password")
            if pin == "1234":
                st.success("גישה אושרה")
                st.code(donor.get('אשראי', 'לא נמצא נתון אשראי'), language="")
            elif pin:
                st.error("קוד שגוי!")

        st.divider()
        st.subheader("📋 היסטוריית תרומות")
        
        filter_h = st.radio("סנן לפי חג:", ["הכל", "פסח", "פורים", "ר''ה", "חנוכה"], horizontal=True)
        
        history = []
        for col in campaign_cols:
            val = donor[col]
            if pd.notna(val) and str(val).strip() not in ["", "nan", "0"]:
                if filter_h == "הכל" or filter_h in col:
                    history.append({"קמפיין": col, "סכום": val})
        
        if history:
            st.table(pd.DataFrame(history))
            st.markdown(f"<h3 style='color:#00b5ad; text-align:left;'>סה''כ מכלול: ₪{donor['מכלול']:,.0f}</h3>", unsafe_allow_html=True)
        else:
            st.info("לא נמצאו תרומות בסינון זה.")
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("מערכת מאובטחת - יד תומך. אנא הכנס סיסמה.")
