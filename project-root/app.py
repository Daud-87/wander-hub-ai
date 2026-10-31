# app.py - ENHANCED VERSION WITH BOOKING SYSTEM & MULTIPLE MODELS
import os
import json
import threading
import pickle
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from jinja2 import TemplateNotFound

# --- Paths & Flask app ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

DATAFILE = os.path.join(BASE_DIR, 'package_dataset_pakistan_01_corrected.csv')
MODEL_FILE = os.path.join(BASE_DIR, 'model_store.pkl')
PAYMENTS_FILE = os.path.join(BASE_DIR, 'payments_store.json')
BOOKINGS_FILE = os.path.join(BASE_DIR, 'bookings_store.json')

TOP_K_DEFAULT = 10
_lock = threading.Lock()

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# --- JSON helpers ---
def _load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return []

def _save_json(path, obj):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving {path}: {e}")

# --- Model utilities ---
def detect_columns(df):
    print("🔍 Detecting columns in dataset...")
    mapping = {
        'id': 'package_id',
        'place': 'place_name', 
        'price': 'avg_price',
        'days': 'duration_days',
        'transport': 'transport',
        'desc': 'tags'
    }
    print(f"📊 Column mapping: {mapping}")
    return mapping

def safe_str(x):
    return '' if pd.isna(x) else str(x)

def safe_num(x):
    try:
        if pd.isna(x): return 0
        return float(x)
    except:
        return 0

class ModelStore:
    def __init__(self):
        self.model = None
        self.mapping = None

    def save(self, path=MODEL_FILE):
        try:
            with open(path, 'wb') as f:
                pickle.dump({'model': self.model, 'mapping': self.mapping}, f)
            print(f"💾 Model saved to {path}")
        except Exception as e:
            print(f"❌ Failed to save model: {e}")

    def load(self, path=MODEL_FILE):
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            self.model = data.get('model')
            self.mapping = data.get('mapping')
            print(f"📂 Model loaded from {path}")
            return True
        except Exception as e:
            print(f'❌ Failed to load model: {e}')
            return False

MS = ModelStore()

def train_model():
    print('🎯 Training model from CSV...')
    
    if not os.path.exists(DATAFILE):
        raise FileNotFoundError(f"Dataset '{DATAFILE}' not found.")

    # Read CSV
    df = pd.read_csv(DATAFILE)
    print(f"📈 Loaded dataset with {len(df)} rows")
    
    # Fill NaN values
    df.fillna('', inplace=True)
    mapping = detect_columns(df)

    # Create working dataframe
    df2 = df.copy()
    
    # Create standardized columns
    df2['__id'] = df2[mapping['id']].astype(str)
    df2['__place'] = df2[mapping['place']].astype(str)
    df2['__price'] = pd.to_numeric(df2[mapping['price']], errors='coerce')
    df2['__days'] = pd.to_numeric(df2[mapping['days']], errors='coerce')
    df2['__transport'] = df2[mapping['transport']].astype(str)
    df2['__desc'] = df2[mapping['desc']].astype(str)

    # Handle missing values
    price_median = df2['__price'].median() if not df2['__price'].isna().all() else 25000
    days_median = df2['__days'].median() if not df2['__days'].isna().all() else 3
    
    df2['__price_filled'] = df2['__price'].fillna(price_median)
    df2['__days_filled'] = df2['__days'].fillna(days_median)

    # Create enhanced text features
    df2['__text'] = (
        df2['__place'] + ' ' + 
        df2['__desc'] + ' ' + 
        df2['__transport'] + ' ' +
        df2['category'].fillna('') + ' ' +
        df2['province'].fillna('') + ' ' +
        df2['accommodation'].fillna('') + ' ' +
        df2['best_season'].fillna('')
    ).str.lower().str.strip()

    # Multiple models for different search strategies
    # 1. TF-IDF for text similarity
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words='english')
    X_text = vectorizer.fit_transform(df2['__text'].values)
    
    # 2. KNN for text
    knn_text = NearestNeighbors(n_neighbors=min(TOP_K_DEFAULT, len(df2)), metric='cosine')
    knn_text.fit(X_text)

    # 3. Numeric features (price and days)
    numeric = df2[['__price_filled', '__days_filled']].values
    scaler = StandardScaler().fit(numeric)
    X_num = scaler.transform(numeric)
    
    # 4. KNN for numeric
    knn_num = NearestNeighbors(n_neighbors=min(TOP_K_DEFAULT, len(df2)), metric='euclidean')
    knn_num.fit(X_num)

    # 5. Content-based with clustering
    kmeans = KMeans(n_clusters=min(10, len(df2)//10), random_state=42)
    clusters = kmeans.fit_predict(X_text)

    model = {
        'df': df2.reset_index(drop=True),
        'vectorizer': vectorizer,
        'knn_text': knn_text,
        'knn_num': knn_num,
        'scaler': scaler,
        'kmeans': kmeans,
        'clusters': clusters
    }

    MS.model = model
    MS.mapping = mapping
    MS.save()
    
    print(f'✅ Training complete. {len(df2)} packages loaded')
    return model

def ensure_model():
    if MS.load():
        if MS.model and 'df' in MS.model and len(MS.model['df']) > 0:
            print(f'📂 Model loaded: {len(MS.model["df"])} packages')
            return MS.model
        else:
            print('🔄 Model file loaded but content missing, retraining...')
    
    try:
        return train_model()
    except Exception as e:
        print(f'❌ Failed to train model: {e}')
        return None

# --- Enhanced Search Logic with Multiple Models ---
def hybrid_search(q_text='', budget=None, days=None, transport=None, model_type='hybrid', top_k=TOP_K_DEFAULT):
    model = MS.model
    if model is None:
        return []
    
    df = model['df']
    n_items = len(df)
    
    if n_items == 0:
        return []
    
    print(f"🔍 Searching: '{q_text}', budget={budget}, days={days}, transport={transport}, model={model_type}")
    
    results = []
    
    if model_type == 'content_knn' or model_type == 'hybrid':
        # Content-based search
        if q_text and q_text.strip():
            try:
                query_vector = model['vectorizer'].transform([q_text.lower()])
                distances, indices = model['knn_text'].kneighbors(query_vector, n_neighbors=min(top_k*2, n_items))
                
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    row = df.iloc[idx]
                    score = (1 - distance) * 0.7
                    
                    # Apply filters
                    if budget:
                        budget_val = float(budget)
                        price_diff = abs(row['__price_filled'] - budget_val)
                        max_price_diff = max(abs(df['__price_filled'] - budget_val))
                        price_score = (1 - (price_diff / max_price_diff)) if max_price_diff > 0 else 1
                        score += price_score * 0.15
                    
                    if days:
                        days_val = float(days)
                        days_diff = abs(row['__days_filled'] - days_val)
                        max_days_diff = max(abs(df['__days_filled'] - days_val))
                        days_score = (1 - (days_diff / max_days_diff)) if max_days_diff > 0 else 1
                        score += days_score * 0.15
                    
                    if transport and transport.strip():
                        if transport.lower() not in str(row['__transport']).lower():
                            score -= 0.3
                    
                    results.append(create_package_result(row, min(1.0, max(0.0, score))))
                    
            except Exception as e:
                print(f"❌ Content search error: {e}")
    
    if (not results or model_type == 'price_knn') and model_type != 'content_knn':
        # Price/days based search
        try:
            q_price = float(budget) if budget else df['__price_filled'].median()
            q_days = float(days) if days else df['__days_filled'].median()
            
            query_num = np.array([[q_price, q_days]])
            query_scaled = model['scaler'].transform(query_num)
            distances, indices = model['knn_num'].kneighbors(query_scaled, n_neighbors=min(top_k, n_items))
            
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                row = df.iloc[idx]
                
                transport_match = True
                if transport and transport.strip():
                    transport_match = transport.lower() in str(row['__transport']).lower()
                
                if transport_match:
                    score = max(0.0, 1 - (distance / distances[0].max())) if distances[0].max() > 0 else 1.0
                    results.append(create_package_result(row, score))
                    
        except Exception as e:
            print(f"❌ Numeric search error: {e}")
    
    # Sort and return
    results.sort(key=lambda x: x['score'], reverse=True)
    final_results = results[:top_k]
    
    print(f"✅ Search completed: {len(final_results)} results found")
    return final_results

def create_package_result(row, score):
    """Create a standardized package result with all details"""
    return {
        'id': str(row['__id']),
        'place': safe_str(row['__place']),
        'price': safe_num(row['__price']),
        'days': safe_num(row['__days']),
        'transport': safe_str(row['__transport']),
        'description': safe_str(row['__desc']),
        'province': safe_str(row.get('province', '')),
        'category': safe_str(row.get('category', '')),
        'accommodation': safe_str(row.get('accommodation', '')),
        'rating': safe_num(row.get('rating', 0)),
        'best_season': safe_str(row.get('best_season', '')),
        'difficulty': safe_str(row.get('difficulty', '')),
        'score': score
    }

# --- Enhanced Routes ---
@app.route('/')
def index():
    try:
        df = MS.model['df'] if MS.model else []
        return render_template('index.html', total=len(df))
    except TemplateNotFound:
        return "❌ Error: index.html not found in templates folder"

@app.route('/search', methods=['POST'])
def search_api():
    try:
        payload = request.json or {}
        q_text = payload.get('q', '') or ''
        budget = payload.get('budget', None)
        days = payload.get('days', None)
        transport = payload.get('transport', None)
        model_type = payload.get('model_type', 'hybrid')
        top_k = int(payload.get('k', TOP_K_DEFAULT))
        
        results = hybrid_search(
            q_text=q_text, 
            budget=budget, 
            days=days, 
            transport=transport,
            model_type=model_type,
            top_k=top_k
        )
        return jsonify({'results': results})
    except Exception as e:
        print(f"❌ Search API error: {e}")
        return jsonify({'results': [], 'error': str(e)}), 500

@app.route('/package/<pkg_id>')
def get_package(pkg_id):
    """Get complete package details for booking page"""
    try:
        if not MS.model:
            return jsonify({'error':'model not loaded'}), 500
        
        df = MS.model['df']
        row = df[df['__id'].astype(str) == str(pkg_id)]
        
        if row.empty:
            return jsonify({'error': 'not found'}), 404
        
        r = row.iloc[0]
        package_details = {
            'id': str(r['__id']),
            'place': safe_str(r['__place']),
            'price': safe_num(r['__price']),
            'days': safe_num(r['__days']),
            'transport': safe_str(r['__transport']),
            'description': safe_str(r['__desc']),
            'province': safe_str(r.get('province', '')),
            'category': safe_str(r.get('category', '')),
            'accommodation': safe_str(r.get('accommodation', '')),
            'rating': safe_num(r.get('rating', 0)),
            'reviews_count': safe_num(r.get('reviews_count', 0)),
            'best_season': safe_str(r.get('best_season', '')),
            'difficulty': safe_str(r.get('difficulty', '')),
            'nearby_city': safe_str(r.get('nearby_city', '')),
            'latitude': safe_num(r.get('latitude', 0)),
            'longitude': safe_num(r.get('longitude', 0)),
            'min_price': safe_num(r.get('min_price', 0)),
            'max_price': safe_num(r.get('max_price', 0)),
            'popularity_score': safe_num(r.get('popularity_score', 0))
        }
        return jsonify(package_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/book-package', methods=['POST'])
def book_package():
    """Handle package booking"""
    try:
        payload = request.json or {}
        
        # Validate required fields
        required_fields = ['packageId', 'packageName', 'email', 'people', 'startDate']
        for field in required_fields:
            if not payload.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        booking_data = {
            'id': 'B' + datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[-12:],
            'packageId': payload['packageId'],
            'packageName': payload['packageName'],
            'customerName': payload.get('customerName', ''),
            'email': payload['email'],
            'phone': payload.get('phone', ''),
            'people': int(payload['people']),
            'totalPrice': float(payload.get('totalPrice', 0)),
            'startDate': payload['startDate'],
            'specialRequests': payload.get('specialRequests', ''),
            'status': 'confirmed',
            'createdAt': datetime.utcnow().isoformat()
        }
        
        # Save booking
        bookings = _load_json(BOOKINGS_FILE)
        bookings.insert(0, booking_data)
        _save_json(BOOKINGS_FILE, bookings)
        
        print(f"📅 Booking created: {booking_data['id']} - {booking_data['packageName']}")
        return jsonify({'status': 'success', 'booking': booking_data, 'message': 'Booking confirmed successfully!'})
        
    except Exception as e:
        print(f"❌ Booking error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/user-bookings/<email>')
def get_user_bookings(email):
    """Get all bookings for a user"""
    try:
        bookings = _load_json(BOOKINGS_FILE)
        user_bookings = [b for b in bookings if b.get('email') == email]
        return jsonify({'bookings': user_bookings})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Existing routes (payments, bookings, etc.)
@app.route('/payments', methods=['GET','POST'])
def payments():
    try:
        if request.method == 'GET':
            payments_data = _load_json(PAYMENTS_FILE)
            return jsonify({'payments': payments_data})
        
        payload = request.json or {}
        payment_data = {
            'id': 'P' + datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[-12:],
            'bookingId': payload.get('bookingId'),
            'customerName': payload.get('customerName', ''),
            'email': payload.get('email', ''),
            'amount': float(payload.get('amount', 0)),
            'method': payload.get('method', 'Credit Card'),
            'status': 'completed',
            'createdAt': datetime.utcnow().isoformat()
        }
        
        payments_arr = _load_json(PAYMENTS_FILE)
        payments_arr.insert(0, payment_data)
        _save_json(PAYMENTS_FILE, payments_arr)
        
        return jsonify({'status':'success','payment': payment_data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug-data')
def debug_data():
    try:
        if not MS.model:
            return jsonify({'error': 'No model loaded'})
        
        df = MS.model['df']
        sample_data = []
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            sample_data.append({
                'id': str(row['__id']),
                'place': safe_str(row['__place']),
                'price': safe_num(row['__price']),
                'days': safe_num(row['__days']),
                'transport': safe_str(row['__transport']),
                'description': safe_str(row['__desc'])
            })
        
        return jsonify({
            'total_records': len(df),
            'sample_data': sample_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:p>')
def static_files(p):
    return send_from_directory(STATIC_DIR, p)

if __name__ == '__main__':
    # Initialize storage files
    if not os.path.exists(PAYMENTS_FILE): 
        _save_json(PAYMENTS_FILE, [])
    
    if not os.path.exists(BOOKINGS_FILE): 
        _save_json(BOOKINGS_FILE, [])
    
    # Ensure model is trained
    print("🚀 Starting Enhanced Pakistan Travel Packages App...")
    ensure_model()
    
    print(f"🎯 Default results per search: {TOP_K_DEFAULT}")
    print("🔧 Available models: hybrid, content_knn, price_knn")
    print("📅 Booking system: Enabled")
    print("🌐 Server starting at http://127.0.0.1:5000")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
    except Exception as e:
        print(f'❌ Failed to start Flask app: {e}')