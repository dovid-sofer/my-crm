import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. הגדרות דף
st.set_page_config(page_title="יד תומך - CRM", layout="wide", initial_sidebar_state="collapsed")

# --- CSS עיצוב נדרים פלוס משופר ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: RTL; text-align: right; }
    
    .top-nav { background-color: #3b566e; color: white; padding: 10px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 4px solid #00b5ad; }
    .icon-bar { background-color: #5591ab; padding: 15px; display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; border-radius: 0 0 20px 20px; }
    
    .nedarim-header { background-color: #00b5ad; color: white; padding: 12px; font-weight: bold; display: flex; border-radius: 8px 8px 0 0; }
    .donor-card { background-color: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); border-right: 12px solid #00b5ad; }
    
    /* עיצוב כפתורי הניווט העליונים */
    .stButton>button { border: none; background: transparent; color: white; padding: 0; }
    .nav-btn { text-align: center; color: white; cursor: pointer; }
    .nav-icon { background: white; color: #5591ab; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-size: 20px; }
    .active .nav-icon { background: #00b5ad; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. לוגיקת נתונים
def clean_money(val):
    if pd.isna(val) or str(val).strip() in ["", "nan", "0"]: return 0.0
    try:
        res = str(val).replace('₪','').replace('$','').replace(',','').strip().split()[0]
        return float(res)
    except: return 0.0

@st.cache_data
def load_initial_data():
    try:
        df = pd.read_csv('donors.csv', encoding='utf-8-sig')
    except:
        df = pd.read_csv('donors.csv', encoding='cp1255')
    df.columns = [c.strip() for c in df.columns]
    return df

# ניהול State (כדי שהשינויים יישמרו במהלך הגלישה)
if 'df' not in st.session_state:
    st.session_state.df = load_initial_data()
if 'page' not in st.session_state:
    st.session_state.page = 'management' # דף ברירת מחדל
if 'selected_idx' not in st.session_state:
    st.session_state.selected_idx = None

df = st.session_state.df

# חישוב מכלול מחדש
personal_cols = ['משפחה', 'פרטי', 'רחוב', 'טלפון', 'טלפון נוסף', 'קהילה', 'אשראי']
campaign_cols = [c for c in df.columns if c not in personal_cols and c != 'מכלול']
df['מכלול'] = df[campaign_cols].apply(lambda col: col.map(clean_money)).sum(axis=1)

# --- סרגל עליון ---
col_logo_1, col_logo_2 = st.columns([1, 8])
with col_logo_1:
    if os.path.exists("logo.png"): st.image("logo.png", width=70)
with col_logo_2:
    st.markdown('<div class="top-nav"><div style="font-size:22px; font-weight:bold;">יד תומך</div><div style="font-size:14px;">שלום, שלמה סופר</div></div>', unsafe_allow_html=True)

# --- סרגל אייקונים פונקציונלי ---
icon_cols = st.columns(5)
with icon_cols[0]:
    if st.button("🏠\nדף הבית"): st.session_state.page = 'home'
with icon_cols[1]:
    if st.button("📊\nדוחות"): st.session_state.page = 'reports'
with icon_cols[2]:
    if st.button("👥\nניהול תורמים"): st.session_state.page = 'management'
with icon_cols[3]:
    if st.button("💳\nסליקה"): st.session_state.page = 'billing'
with icon_cols[4]:
    if st.button("⚙️\nהגדרות"): st.session_state.page = 'settings'

# --- אבטחה ---
password = st.sidebar.text_input("סיסמת מערכת", type="password")
if password == "dudi330582008":

    # --- דף הבית (סיכום) ---
    if st.session_state.page == 'home':
        st.title("ברוך הבא למערכת יד תומך")
        c1, c2, c3 = st.columns(3)
        c1.metric("סה''כ תורמים", len(df))
        c2.metric("סה''כ גיוס כללי", f"₪{df['מכלול'].sum():,.0f}")
        c3.metric("קמפיין אחרון", campaign_cols[-1])

    # --- דף דוחות (סטטיסטיקה) ---
    elif st.session_state.page == 'reports':
        st.header("📊 סטטיסטיקות גיוס")
        holiday = st.selectbox("בחר חג לניתוח:", ["פסח", "פורים", "ר''ה", "חנוכה"])
        stats = []
        for col in campaign_cols:
            if holiday in col:
                stats.append({"קמפיין": col, "סכום": df[col].map(clean_money).sum()})
        if stats:
            fig = px.bar(pd.DataFrame(stats), x="קמפיין", y="סכום", color_discrete_sequence=['#00b5ad'])
            st.plotly_chart(fig, use_container_width=True)

    # --- דף ניהול תורמים (הטבלה) ---
    elif st.session_state.page == 'management':
        if st.session_state.selected_idx is None:
            st.subheader("🔍 חיפוש וניהול תורמים")
            search = st.text_input("", placeholder="חפש שם, טלפון או כתובת...")
            
            st.markdown('<div class="nedarim-header"><div style="flex:1.5">מכלול</div><div style="flex:3">שם התורם</div><div style="flex:3">כתובת</div><div style="flex:2">טלפון</div><div style="flex:1">פעולה</div></div>', unsafe_allow_html=True)
            
            view_df = df
            if search: view_df = df[df.apply(lambda r: search in str(r.values), axis=1)]
            
            for i, row in view_df.iterrows():
                cols = st.columns([1.5, 3, 3, 2, 1])
                cols[0].write(f"**₪{row['מכלול']:,.0f}**")
                cols[1].write(f"{row['משפחה']} {row['פרטי']}")
                cols[2].write(row['רחוב'] if pd.notna(row['רחוב']) else "---")
                cols[3].write(row['טלפון'] if pd.notna(row['טלפון']) else "---")
                if cols[4].button("ערוך ✏️", key=f"edit_{i}"):
                    st.session_state.selected_idx = i
                    st.rerun()
        
        # --- כרטיס תורם (עריכה וחיוב) ---
        else:
            idx = st.session_state.selected_idx
            donor = df.loc[idx]
            
            if st.button("⬅️ חזרה לרשימה"):
                st.session_state.selected_idx = None
                st.rerun()

            st.markdown('<div class="donor-card">', unsafe_allow_html=True)
            st.header(f"✏️ עריכת תורם: {donor['משפחה']} {donor['פרטי']}")
            
            with st.form("edit_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_ln = st.text_input("שם משפחה", value=donor['משפחה'])
                    new_fn = st.text_input("שם פרטי", value=donor['פרטי'])
                    new_addr = st.text_input("כתובת", value=donor['רחוב'])
                with col2:
                    new_p1 = st.text_input("טלפון", value=donor['טלפון'])
                    new_p2 = st.text_input("טלפון נוסף", value=donor['טלפון נוסף'])
                    new_comm = st.text_input("קהילה", value=donor['קהילה'])
                
                if st.form_submit_button("💾 שמור שינויים בפרטים"):
                    st.session_state.df.at[idx, 'משפחה'] = new_ln
                    st.session_state.df.at[idx, 'פרטי'] = new_fn
                    st.session_state.df.at[idx, 'רחוב'] = new_addr
                    st.session_state.df.at[idx, 'טלפון'] = new_p1
                    st.session_state.df.at[idx, 'טלפון נוסף'] = new_p2
                    st.session_state.df.at[idx, 'קהילה'] = new_comm
                    st.success("הפרטים עודכנו!")

            st.divider()
            st.subheader("➕ הוספת חיוב/תרומה חדשה")
            with st.form("add_donation"):
                camp = st.selectbox("בחר קמפיין:", campaign_cols)
                amount = st.text_input("סכום לחיוב (למשל: 150 ₪):")
                if st.form_submit_button("➕ הוסף חיוב"):
                    st.session_state.df.at[idx, camp] = amount
                    st.success(f"חיוב על סך {amount} נוסף לקמפיין {camp}!")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # כפתור הורדת הגיבוי (כי אנחנו ב-CSV)
            st.write("")
            csv = st.session_state.df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 הורד קובץ מעודכן (לשמירה קבועה)", csv, "donors_updated.csv", "text/csv")

else:
    st.info("אנא הכנס סיסמה.")
