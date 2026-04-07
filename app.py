import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. הגדרות דף
st.set_page_config(page_title="יד תומך - ניהול תורמים", layout="wide", initial_sidebar_state="collapsed")

# --- הזרקת העיצוב המדויק של נדרים פלוס (Tailwind + Custom CSS) ---
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@200;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stApp { background-color: #f7fafc; }
    
    /* Header & Nav */
    .nedarim-header { background-color: #3b566e; color: white; padding: 15px 25px; display: flex; justify-content: space-between; align-items: center; border-bottom: 4px solid #00b5ad; }
    .icon-bar { background-color: #5591ab; padding: 10px; display: flex; justify-content: center; gap: 30px; border-radius: 0 0 20px 20px; margin-bottom: 25px; }
    .nav-icon-circle { background: white; color: #5591ab; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 5px; }
    .active .nav-icon-circle { background: #00b5ad; color: white; }

    /* Table */
    .nedarim-table-head { background-color: #00b5ad; color: white; font-weight: bold; padding: 12px; border-radius: 8px 8px 0 0; }
    .table-row { background: white; border-bottom: 1px solid #edf2f7; transition: 0.2s; }
    .table-row:hover { background-color: #f1fafa; }

    /* Donor Card Modal */
    .donor-modal { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.15); border-right: 12px solid #00b5ad; }
    .michlol-box { background: rgba(0, 181, 173, 0.1); border: 1px solid rgba(0, 181, 173, 0.2); border-radius: 15px; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
    .input-label { font-size: 13px; color: #718096; font-weight: 600; margin-bottom: 4px; }
    .input-field { background: #edf2f7; border: none; padding: 10px; border-radius: 8px; width: 100%; margin-bottom: 15px; }
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
    return df

# ניהול מצבי דפים
if 'df' not in st.session_state: st.session_state.df = load_data()
if 'page' not in st.session_state: st.session_state.page = 'management'
if 'selected_donor' not in st.session_state: st.session_state.selected_donor = None

df = st.session_state.df
personal_cols = ['משפחה', 'פרטי', 'רחוב', 'טלפון', 'טלפון נוסף', 'קהילה', 'אשראי']
campaign_cols = [c for c in df.columns if c not in personal_cols]

# חישוב מכלול
df['מכלול'] = df[campaign_cols].apply(lambda col: col.map(clean_money)).sum(axis=1)

# --- הצגת Header ---
st.markdown(f"""
<div class="nedarim-header">
    <div style="display:flex; align-items:center; gap:15px;">
        <span style="font-size:24px; font-weight:800;">יד תומך</span>
    </div>
    <div style="font-size:14px; opacity:0.8;">שלום, מנהל המערכת | יציאה</div>
</div>
""", unsafe_allow_html=True)

# --- סרגל אייקונים (ניווט) ---
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1,1,1,1,1])
with nav_col1: 
    if st.button("🏠\\nדף הבית"): st.session_state.page = 'dashboard'
with nav_col2: 
    if st.button("📊\\nדוחות"): st.session_state.page = 'reports'
with nav_col3: 
    if st.button("👥\\nניהול תורמים"): st.session_state.page = 'management'
with nav_col4: 
    if st.button("💳\\nסליקה"): st.session_state.page = 'billing'
with nav_col5: 
    if st.button("⚙️\\nהגדרות"): st.session_state.page = 'settings'

# --- אבטחת כניסה ---
password = st.sidebar.text_input("סיסמת יד תומך", type="password")
if password == "dudi330582008":

    # --- דף דאשבורד ---
    if st.session_state.page == 'dashboard':
        st.markdown("<h2 class='text-2xl font-bold text-[#3b566e] mb-6'>לוח בקרה כללי</h2>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("סה''כ גיוס", f"₪{df['מכלול'].sum():,.0f}")
        c2.metric("תורמים רשומים", len(df))
        c3.metric("ממוצע תרומה", f"₪{df['מכלול'].mean():,.0f}")
        c4.metric("קמפיין נוכחי", campaign_cols[-1])
        
        # גרף תרומות לפי חגים
        totals = df[campaign_cols].apply(lambda col: col.map(clean_money)).sum()
        fig = px.bar(x=totals.index, y=totals.values, title="הכנסות לפי קמפיינים", color_discrete_sequence=['#00b5ad'])
        st.plotly_chart(fig, use_container_width=True)

    # --- דף ניהול תורמים (הטבלה) ---
    elif st.session_state.page == 'management' and st.session_state.selected_donor is None:
        st.markdown("<h2 class='text-2xl font-bold text-[#3b566e] mb-4'>ניהול אנשי קשר</h2>", unsafe_allow_html=True)
        search = st.text_input("", placeholder="חפש תורם לפי שם, כתובת או טלפון...")
        
        # בניית הטבלה הטורקיזית
        st.markdown('<div class="nedarim-table-head"><div class="flex justify-between"> <span style="flex:1">מכלול</span> <span style="flex:3">שם התורם</span> <span style="flex:3">כתובת</span> <span style="flex:2">טלפון</span> <span style="flex:1">ערוך</span> </div></div>', unsafe_allow_html=True)
        
        view_df = df
        if search:
            view_df = df[df.apply(lambda r: search in str(r.values), axis=1)]

        for i, row in view_df.iterrows():
            r_col = st.columns([1, 3, 3, 2, 1])
            r_col[0].write(f"**₪{row['מכלול']:,.0f}**")
            r_col[1].write(f"{row['משפחה']} {row['פרטי']}")
            r_col[2].write(row['רחוב'] if pd.notna(row['רחוב']) else "---")
            r_col[3].write(row['טלפון'])
            if r_col[4].button("✏️", key=f"edit_{i}"):
                st.session_state.selected_donor = i
                st.rerun()

    # --- כרטיס תורם (ה-Popup המעוצב) ---
    elif st.session_state.selected_donor is not None:
        idx = st.session_state.selected_donor
        donor = df.loc[idx]
        
        if st.button("⬅️ חזרה לרשימת תורמים"):
            st.session_state.selected_donor = None
            st.rerun()

        st.markdown('<div class="donor-modal">', unsafe_allow_html=True)
        st.markdown(f"<h2 class='text-2xl font-bold text-[#3b566e] mb-6'>👤 כרטיס תורם: {donor['משפחה']} {donor['פרטי']}</h2>", unsafe_allow_html=True)
        
        # חלוקה ל-2 טורים בדיוק כמו בעיצוב של גוגל
        card_c1, card_c2 = st.columns(2)
        
        with card_c1: # צד ימין - זהות
            st.markdown('<p class="input-label">שם משפחה</p>', unsafe_allow_html=True)
            new_ln = st.text_input("", value=donor['משפחה'], key="eln", label_visibility="collapsed")
            st.markdown('<p class="input-label">שם פרטי</p>', unsafe_allow_html=True)
            new_fn = st.text_input("", value=donor['פרטי'], key="efn", label_visibility="collapsed")
            st.markdown('<p class="input-label">כתובת מגורים</p>', unsafe_allow_html=True)
            new_addr = st.text_input("", value=donor['רחוב'], key="eadr", label_visibility="collapsed")
            
            # קופסת מכלול בולטת
            st.markdown(f"""
            <div class="michlol-box">
                <div><h4 style="color:#00b5ad; font-weight:bold; margin:0;">סה"כ מכלול</h4><p style="font-size:12px; margin:0;">יתרת תרומות מצטברת</p></div>
                <div style="font-size:32px; font-weight:900; color:#00b5ad;">₪{donor['מכלול']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        with card_c2: # צד שמאל - קשר ואשראי
            st.markdown('<p class="input-label">טלפון נייד</p>', unsafe_allow_html=True)
            new_p1 = st.text_input("", value=donor['טלפון'], key="ep1", label_visibility="collapsed")
            st.markdown('<p class="input-label">קהילה</p>', unsafe_allow_html=True)
            new_comm = st.text_input("", value=donor['קהילה'], key="ecomm", label_visibility="collapsed")
            
            st.divider()
            # אבטחת אשראי
            st.markdown('<p class="text-sm font-bold text-red-500 mb-2">🔒 אבטחת כרטיס אשראי</p>', unsafe_allow_html=True)
            with st.popover("💳 הצג פרטי כרטיס אשראי"):
                pin = st.text_input("הזן קוד PIN:", type="password")
                if pin == "1234":
                    st.success("גישה אושרה")
                    st.code(donor.get('אשראי', 'לא הוזן כרטיס'), language="")
                elif pin:
                    st.error("קוד שגוי")
        
        # שמירה והוספת תרומה
        st.write("")
        if st.button("💾 שמור שינויים בפרטים", use_container_width=True):
            st.session_state.df.at[idx, 'משפחה'] = new_ln
            st.session_state.df.at[idx, 'פרטי'] = new_fn
            st.session_state.df.at[idx, 'רחוב'] = new_addr
            st.session_state.df.at[idx, 'טלפון'] = new_p1
            st.session_state.df.at[idx, 'קהילה'] = new_comm
            st.success("הנתונים עודכנו!")

        st.markdown("---")
        st.subheader("📋 היסטוריית תרומות וחיוב חדש")
        
        # הוספת תרומה חדשה
        with st.expander("➕ הוספת תרומה חדשה לקמפיין"):
            sel_camp = st.selectbox("בחר קמפיין:", campaign_cols)
            new_amt = st.text_input("סכום (₪):")
            if st.button("עדכן תרומה"):
                st.session_state.df.at[idx, sel_camp] = new_amt
                st.rerun()

        # טבלת היסטוריה
        hist_list = []
        for c in campaign_cols:
            val = donor[c]
            if pd.notna(val) and str(val).strip() not in ["", "0", "nan"]:
                hist_list.append({"קמפיין": c, "סכום": val})
        if hist_list:
            st.table(pd.DataFrame(hist_list))
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("אנא הכנס סיסמת מערכת כדי להתחיל.")
