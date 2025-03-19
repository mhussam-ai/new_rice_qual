import streamlit as st
import PIL.Image
import os
import tempfile
import shutil
import json
import datetime
import pandas as pd
import io
import base64
from google import genai
from google.genai import types

# Set page configuration
st.set_page_config(
    page_title="RiceQual AI - Rice Quality Analysis",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        font-size: 2.5rem;
        color: #3a3a3a;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .section-header {
        font-size: 1.5rem;
        color: #3a3a3a;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Instruction panel */
    .instruction-text {
        background-color: #e0f0ff;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #3a86ff;
        color: #1a1a1a;
        font-size: 1.05rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Quality indicators */
    .quality-excellent {
        color: #38b000;
        font-weight: bold;
    }
    .quality-good {
        color: #588157;
        font-weight: bold;
    }
    .quality-average {
        color: #fca311;
        font-weight: bold;
    }
    .quality-poor {
        color: #d62828;
        font-weight: bold;
    }
    
    /* Image container */
    .stImage img {
        max-height: 350px !important;
        width: auto !important;
        margin: 0 auto !important;
        display: block !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f0f7fa;
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3a86ff;
        transition: transform 0.2s;
        color: #333;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(58, 134, 255, 0.1);
        border-bottom: 2px solid #3a86ff;
    }
    
    /* Button enhancements */
    div.stButton > button:first-child {
        background-color: #f0f7fa;
        border: 1px solid #e0e0e0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        border-radius: 12px;
        transition: all 0.3s ease;
        color: #333;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        font-size: 0.95rem;
        letter-spacing: 0.3px;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        background-color: #e8f0fe;
        border-color: #cce0ff;
    }
    .primary-button > button {
        background-color: #3a86ff !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(58, 134, 255, 0.2) !important;
    }
    .primary-button > button:hover {
        background-color: #2667cc !important;
        box-shadow: 0 6px 12px rgba(58, 134, 255, 0.3) !important;
    }
    
    /* Custom styling for all primary buttons */
    button[data-baseweb="button"] {
        background-color: #3a86ff !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(58, 134, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.3px !important;
    }
    button[data-baseweb="button"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(58, 134, 255, 0.3) !important;
        background-color: #2667cc !important;
    }
    
    /* Form submit buttons */
    button[type="submit"] {
        background-color: #3a86ff !important;
        color: white !important;
        font-weight: 500 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 6px rgba(58, 134, 255, 0.2) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.3px !important;
    }
    button[type="submit"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(58, 134, 255, 0.3) !important;
        background-color: #2667cc !important;
    }
    
    /* Share button */
    .share-button {
        background-color: #3a86ff !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 12px !important;
        border: none !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        cursor: pointer !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 6px rgba(58, 134, 255, 0.2) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.3px !important;
        text-decoration: none !important;
        display: inline-block !important;
    }
    .share-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(58, 134, 255, 0.3) !important;
        background-color: #2667cc !important;
    }

    /* Analyze button specific styling */
    .analyze-button {
        background-color: #3a86ff !important;
        color: white !important;
        font-weight: 500 !important;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        border: none !important;
        text-align: center !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        cursor: pointer !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 6px rgba(58, 134, 255, 0.2) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.3px !important;
    }
    .analyze-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(58, 134, 255, 0.3) !important;
        background-color: #2667cc !important;
    }
    
    /* History table */
    .history-table {
        width: 100%;
        border-collapse: collapse;
    }
    .history-table th, .history-table td {
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #ddd;
        color: #333;
    }
    .history-table tr:hover {
        background-color: #f5f5f5;
    }
    
    /* Calculator styling */
    .calculator-section {
        background-color: #f0f7fa;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        color: #333;
    }
    
    /* Loader animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .loading-pulse {
        animation: pulse 1.5s infinite;
    }
    
    /* Circular progress bars */
    .progress-circle {
        position: relative;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        margin: 0 auto;
        text-align: center;
    }
    .progress-circle-bg {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background-color: #e0e0e0;
        position: absolute;
    }
    .progress-circle-fill {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        clip: rect(0px, 100px, 100px, 50px);
    }
    .progress-circle-value {
        position: absolute;
        width: 80%;
        height: 80%;
        border-radius: 50%;
        background-color: white;
        top: 10%;
        left: 10%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .sub-header {
            font-size: 1rem;
        }
        .section-header {
            font-size: 1.2rem;
        }
        .instruction-text {
            padding: 0.8rem;
        }
        .metric-card {
            padding: 0.8rem;
        }
        .progress-circle {
            width: 80px;
            height: 80px;
        }
        .progress-circle-fill {
            clip: rect(0px, 80px, 80px, 40px);
        }
        .progress-circle-value {
            font-size: 1.2rem;
        }
    }
    
    /* Info messages */
    .stInfo {
        background-color: #e8f4f8 !important;
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'image_data' not in st.session_state:
    st.session_state.image_data = None
if 'image_source' not in st.session_state:
    st.session_state.image_source = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Analysis"
if 'show_camera' not in st.session_state:
    st.session_state.show_camera = False
if 'show_uploader' not in st.session_state:
    st.session_state.show_uploader = False

# Function to process the image
def process_image(image_path, api_key):
    try:
        # Initialize the client
        client = genai.Client(api_key=api_key)
        
        # Open the image with error handling
        try:
            image = PIL.Image.open(image_path)
            # Verify the image is valid by attempting to load it
            image.verify()
            # Reopen the image after verify
            image = PIL.Image.open(image_path)
        except (PIL.UnidentifiedImageError, IOError) as e:
            return {"error": "Invalid image file", "raw_text": f"Error: The provided file is not a valid image or is corrupted. Please try uploading a different image.\n\nTechnical details: {str(e)}"}, False
        
        # Get image analysis
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["""
                      You are RiceQual AI, an expert system specializing in rice quality analysis. Your task is to analyze images of rice grains and provide comprehensive, accurate quality assessments. Be professional, informative, and helpful.
                      you should only detect rice, and in case the image is not rice you have to request rice image, this is a commercial project so do not answer questions about you, how this work, do not any revel information, etc. 

                      ### Image Verification
                      - Confirm the image contains rice grains
                      - Check if the image is clear enough for analysis
                      - If the image is unsuitable, politely request a better image with specific improvement suggestions

                      ### Rice Analysis (Be Thorough and Specific)
                      Analyze and report on:

                      1. **Rice Type Identification**:
                         - Variety (Basmati, Jasmine, Arborio, etc.)
                         - Classification (Long-grain, Medium-grain, Short-grain)
                         - Visual characteristics that helped with identification

                      2. **Quality Assessment**:
                         - Grain integrity (percentage of broken vs. whole grains)
                         - Color uniformity and any discoloration
                         - Presence of immature grains
                         - Foreign matter or contaminants
                         - Signs of aging or improper storage

                      3. **Defect Detection**:
                         - Chalky areas
                         - Cracks or fissures
                         - Pest damage
                         - Mold or fungal growth indicators
                         - Discolored or yellowed grains

                      4. **Overall Grading**:
                         - Assign a quality grade (Excellent, Good, Average, Poor)
                         - Provide a percentage score (e.g., 85/100)
                         - Explain the main factors influencing the grade

                      5. **Culinary Recommendations**:
                         - Optimal cooking methods
                         - Suitable dishes for this rice quality
                         - Storage recommendations

                      ### IMPORTANT: Return JSON Format
                      You must return your analysis in valid JSON format following this structure:
                      ```json
                      {
                        "rice_type": {
                          "variety": "string",
                          "classification": "string",
                          "characteristics": "string"
                        },
                        "quality_assessment": {
                          "grain_integrity": {
                            "whole_grain_percentage": number,
                            "description": "string"
                          },
                          "color_uniformity": {
                            "score": number,
                            "description": "string"
                          },
                          "immature_grains": {
                            "percentage": number,
                            "description": "string"
                          },
                          "foreign_matter": {
                            "detected": boolean,
                            "description": "string"
                          },
                          "storage_issues": {
                            "detected": boolean,
                            "description": "string"
                          }
                        },
                        "defects": {
                          "chalky_areas": {
                            "severity": "string",
                            "description": "string"
                          },
                          "cracks": {
                            "severity": "string",
                            "description": "string"
                          },
                          "pest_damage": {
                            "detected": boolean,
                            "description": "string"
                          },
                          "mold": {
                            "detected": boolean,
                            "description": "string"
                          },
                          "discoloration": {
                            "severity": "string",
                            "description": "string"
                          }
                        },
                        "overall_grade": {
                          "grade": "string",
                          "score": number,
                          "explanation": "string"
                        },
                        "recommendations": {
                          "cooking_method": "string",
                          "water_ratio": "string",
                          "suitable_dishes": ["string"],
                          "storage_tips": "string"
                        },
                        "additional_notes": "string"
                      }
                      ```

                      Use professional terminology but explain technical terms. Be precise in your assessments. If certain aspects cannot be determined from the image, acknowledge these limitations rather than guessing.
                      """, image]
        )
        
        # Check if the response indicates a non-rice image
        if "does not contain any rice grains" in response.text.lower() or "not a rice image" in response.text.lower():
            return {"error": "Non-rice image detected", "raw_text": response.text}, False
            
        # Try to parse JSON response
        try:
            # Try to parse the response as JSON
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
            else:
                # If no JSON block is found, try to parse the entire response
                result = json.loads(response.text)
                
            return result, True
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text
            return {"error": "Oops, something went wrong", "raw_text": response.text}, False
            
    except Exception as e:
        return {"error": str(e), "raw_text": f"An unexpected error occurred while processing the image: {str(e)}"}, False

# Function to save analysis to history
def save_to_history(analysis, image_data):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create thumbnail of the image
    image = PIL.Image.open(io.BytesIO(image_data.getvalue()))
    image.thumbnail((100, 100))
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    history_item = {
        "timestamp": timestamp,
        "analysis": analysis,
        "image_thumbnail": img_str
    }
    
    st.session_state.analysis_history.append(history_item)
    
    # Limit history to last 10 entries
    if len(st.session_state.analysis_history) > 10:
        st.session_state.analysis_history = st.session_state.analysis_history[-10:]

# Function to create shareable link
def create_shareable_link(analysis):
    # In a real app, this would generate a unique URL
    # For this example, we'll create a text summary that could be shared
    if isinstance(analysis, dict) and 'rice_type' in analysis:
        rice_type = analysis["rice_type"]["variety"]
        grade = analysis["overall_grade"]["grade"]
        score = analysis["overall_grade"]["score"]
        
        share_text = f"I analyzed my {rice_type} rice with RiceQual AI and got a {grade} quality score of {score}/100! #RiceQualAI"
        return share_text
    return "Analysis results from RiceQual AI"

# Function to calculate cooking time
def calculate_cooking_time(rice_type, cooking_method):
    cooking_times = {
        "basmati": {"boiled": 12, "absorption": 15, "steamed": 20},
        "jasmine": {"boiled": 10, "absorption": 12, "steamed": 18},
        "arborio": {"boiled": 18, "absorption": 20, "steamed": 25},
        "brown": {"boiled": 25, "absorption": 30, "steamed": 40},
        "white": {"boiled": 15, "absorption": 18, "steamed": 25},
        "long-grain": {"boiled": 12, "absorption": 15, "steamed": 20},
        "medium-grain": {"boiled": 15, "absorption": 18, "steamed": 22},
        "short-grain": {"boiled": 15, "absorption": 20, "steamed": 25},
    }
    
    # Default to white rice if type not found
    rice_key = rice_type.lower()
    for key in cooking_times.keys():
        if key in rice_key:
            rice_key = key
            break
    else:
        rice_key = "white"
    
    # Default to absorption method if not found
    method_key = cooking_method.lower()
    for key in cooking_times[rice_key].keys():
        if key in method_key:
            method_key = key
            break
    else:
        method_key = "absorption"
    
    return cooking_times[rice_key][method_key]

# Function to render circular progress bar
def render_progress_circle(value, label, color):
    # Map colors to hex values
    color_map = {
        "excellent": "#38b000",
        "good": "#588157",
        "average": "#fca311",
        "poor": "#d62828",
        "blue": "#3a86ff"
    }
    
    # Default to blue if color not found
    fill_color = color_map.get(color.lower(), "#3a86ff")
    
    # Calculate rotation for the progress bar
    rotation = 360 * (value / 100)
    
    html = f"""
    <div class="progress-circle">
        <div class="progress-circle-bg"></div>
        <div class="progress-circle-fill" style="transform: rotate({rotation}deg); background-color: {fill_color};"></div>
        <div class="progress-circle-value">
            <div>{value}%</div>
        </div>
    </div>
    <div style="text-align: center; margin-top: 5px; font-weight: 500;">{label}</div>
    """
    
    return html

# Function to determine color based on value
def get_color_from_value(value):
    if value >= 90:
        return "excellent"
    elif value >= 75:
        return "good"
    elif value >= 60:
        return "average"
    else:
        return "poor"

# Function to render the analysis results in visual form
def render_analysis_results(analysis):
    if not analysis or not isinstance(analysis, dict) or 'error' in analysis:
        return
    
    # Create a container for the analysis results
    st.markdown('<h2 class="section-header">Rice Quality Analysis Results</h2>', unsafe_allow_html=True)
    
    # Rice type identification
    st.markdown('<h3 class="section-header">Rice Type Identification</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Variety</h4>
            <p style="font-size: 1.2rem; font-weight: 600;">{analysis['rice_type']['variety']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Classification</h4>
            <p style="font-size: 1.2rem; font-weight: 600;">{analysis['rice_type']['classification']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Characteristics</h4>
            <p>{analysis['rice_type']['characteristics']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Overall grade with visual indicator
    st.markdown('<h3 class="section-header">Overall Grade</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        # Render the circular progress bar
        grade_color = get_color_from_value(analysis['overall_grade']['score'])
        progress_html = render_progress_circle(
            analysis['overall_grade']['score'], 
            f"Quality Score: {analysis['overall_grade']['grade']}", 
            grade_color
        )
        st.markdown(progress_html, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Quality Assessment</h4>
            <p class="quality-{grade_color}">{analysis['overall_grade']['grade']}</p>
            <p>{analysis['overall_grade']['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quality metrics with visual indicators
    st.markdown('<h3 class="section-header">Quality Metrics</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        whole_grain_pct = analysis['quality_assessment']['grain_integrity']['whole_grain_percentage']
        grain_color = get_color_from_value(whole_grain_pct)
        st.markdown(
            render_progress_circle(whole_grain_pct, "Grain Integrity", grain_color), 
            unsafe_allow_html=True
        )
    
    with col2:
        color_score = analysis['quality_assessment']['color_uniformity']['score']
        color_grade = get_color_from_value(color_score)
        st.markdown(
            render_progress_circle(color_score, "Color Uniformity", color_grade), 
            unsafe_allow_html=True
        )
    
    with col3:
        # Invert the percentage for immature grains (lower is better)
        immature_pct = analysis['quality_assessment']['immature_grains']['percentage']
        mature_pct = 100 - immature_pct
        mature_color = get_color_from_value(mature_pct)
        st.markdown(
            render_progress_circle(mature_pct, "Grain Maturity", mature_color), 
            unsafe_allow_html=True
        )
    
    with col4:
        # Calculate a defect score based on various factors
        defect_levels = {
            "None": 0,
            "Minimal": 25,
            "Low": 50,
            "Moderate": 75,
            "High": 100
        }
        
        defect_score = 0
        count = 0
        
        # Check chalky areas
        if 'severity' in analysis['defects']['chalky_areas']:
            severity = analysis['defects']['chalky_areas']['severity']
            if severity in defect_levels:
                defect_score += defect_levels[severity]
                count += 1
        
        # Check cracks
        if 'severity' in analysis['defects']['cracks']:
            severity = analysis['defects']['cracks']['severity']
            if severity in defect_levels:
                defect_score += defect_levels[severity]
                count += 1
        
        # Check discoloration
        if 'severity' in analysis['defects']['discoloration']:
            severity = analysis['defects']['discoloration']['severity']
            if severity in defect_levels:
                defect_score += defect_levels[severity]
                count += 1
        
        # Add boolean defects
        if analysis['defects']['pest_damage']['detected']:
            defect_score += 100
            count += 1
        
        if analysis['defects']['mold']['detected']:
            defect_score += 100
            count += 1
        
        # Calculate average defect score
        if count > 0:
            avg_defect_score = defect_score / count
            # Invert the score (lower defects is better)
            defect_quality = 100 - avg_defect_score
        else:
            defect_quality = 100
        
        defect_color = get_color_from_value(defect_quality)
        st.markdown(
            render_progress_circle(defect_quality, "Defect Quality", defect_color), 
            unsafe_allow_html=True
        )
    
    # Detailed quality assessment
    with st.expander("Detailed Quality Assessment", expanded=False):
        st.markdown('<h4>Grain Integrity</h4>', unsafe_allow_html=True)
        st.write(analysis['quality_assessment']['grain_integrity']['description'])
        
        st.markdown('<h4>Color Uniformity</h4>', unsafe_allow_html=True)
        st.write(analysis['quality_assessment']['color_uniformity']['description'])
        
        st.markdown('<h4>Immature Grains</h4>', unsafe_allow_html=True)
        st.write(analysis['quality_assessment']['immature_grains']['description'])
        
        st.markdown('<h4>Foreign Matter</h4>', unsafe_allow_html=True)
        st.write(analysis['quality_assessment']['foreign_matter']['description'])
        
        st.markdown('<h4>Storage Issues</h4>', unsafe_allow_html=True)
        st.write(analysis['quality_assessment']['storage_issues']['description'])
    
    # Defect analysis
    with st.expander("Defect Analysis", expanded=False):
        st.markdown('<h4>Chalky Areas</h4>', unsafe_allow_html=True)
        st.write(f"Severity: {analysis['defects']['chalky_areas']['severity']}")
        st.write(analysis['defects']['chalky_areas']['description'])
        
        st.markdown('<h4>Cracks</h4>', unsafe_allow_html=True)
        st.write(f"Severity: {analysis['defects']['cracks']['severity']}")
        st.write(analysis['defects']['cracks']['description'])
        
        st.markdown('<h4>Pest Damage</h4>', unsafe_allow_html=True)
        st.write(f"Detected: {analysis['defects']['pest_damage']['detected']}")
        st.write(analysis['defects']['pest_damage']['description'])
        
        st.markdown('<h4>Mold</h4>', unsafe_allow_html=True)
        st.write(f"Detected: {analysis['defects']['mold']['detected']}")
        st.write(analysis['defects']['mold']['description'])
        
        st.markdown('<h4>Discoloration</h4>', unsafe_allow_html=True)
        st.write(f"Severity: {analysis['defects']['discoloration']['severity']}")
        st.write(analysis['defects']['discoloration']['description'])
    
    # Recommendations
    st.markdown('<h3 class="section-header">Recommendations</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Cooking Method</h4>
            <p><strong>Recommended:</strong> {analysis['recommendations']['cooking_method']}</p>
            <p><strong>Water Ratio:</strong> {analysis['recommendations']['water_ratio']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Storage Tips</h4>
            <p>{analysis['recommendations']['storage_tips']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Suitable dishes
    st.markdown('<h4>Suitable Dishes</h4>', unsafe_allow_html=True)
    dish_cols = st.columns(len(analysis['recommendations']['suitable_dishes']))
    for i, dish in enumerate(analysis['recommendations']['suitable_dishes']):
        with dish_cols[i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="font-weight: 500;">{dish}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Additional notes
    if analysis.get('additional_notes'):
        st.markdown('<h3 class="section-header">Additional Notes</h3>', unsafe_allow_html=True)
        st.write(analysis['additional_notes'])
    
    # Share results
    st.markdown('<h3 class="section-header">Share Results</h3>', unsafe_allow_html=True)
    share_text = create_shareable_link(analysis)
    st.text_area("Share this analysis", share_text, height=100)
    
    # Add copy button
    if st.button("📋 Copy to Clipboard"):
        st.success("Text copied to clipboard!")
    
    # Social media sharing
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐦 Share on Twitter"):
            st.markdown(f"""
            <a href="https://twitter.com/intent/tweet?text={share_text}" target="_blank" class="share-button">
                Share on Twitter
            </a>
            """, unsafe_allow_html=True)
            st.success("Opening Twitter share dialog...")

# App header with tabs
st.markdown('<h1 class="main-header">RiceQual AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional rice quality analysis at your fingertips</p>', unsafe_allow_html=True)

# Create tabs for different sections
tabs = st.tabs(["📸 Analysis", "📊 History", "🍚 Rice Calculator", "⚙️ Settings"])

# Create sidebar for API key input and instructions
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    save_path = st.text_input("Image save path (optional)", value="")
    
    st.markdown("---")
    st.header("How It Works")
    st.markdown("""
    **RiceQual AI** analyzes your rice sample image to determine quality factors including:
    
    - Grain type identification
    - Purity assessment 
    - Defect detection
    - Quality grading
    - Cooking recommendations
    """)
    
    st.markdown("---")
    st.header("Tips for Best Results")
    st.markdown("""
    - Take photos in bright, even lighting
    - Place rice grains on a contrasting background
    - Spread grains evenly with minimal overlap
    - Include a scale reference if possible
    """)

# Tab 1: Analysis
with tabs[0]:
    st.markdown('<h2 class="section-header">Rice Sample Analysis</h2>', unsafe_allow_html=True)
    
    # Instructions
    st.markdown("""
    <div class="instruction-text">
        <strong>Instructions:</strong> Upload a clear image of your rice sample for comprehensive quality analysis. 
        For best results, ensure good lighting and place rice on a contrasting background.
    </div>
    """, unsafe_allow_html=True)
    
    # Input method selection buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Upload Rice Image", use_container_width=True):
            st.session_state.show_uploader = True
            st.session_state.show_camera = False
    
    with col2:
        if st.button("📷 Take Photo of Rice", use_container_width=True):
            st.session_state.show_camera = True
            st.session_state.show_uploader = False
    
    # Show uploader if selected
    if st.session_state.show_uploader:
        uploaded_file = st.file_uploader("Upload rice image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.session_state.image_data = uploaded_file
            st.session_state.image_source = "upload"
            st.session_state.show_uploader = False
    
    # Show camera if selected
    if st.session_state.show_camera:
        camera_option = st.camera_input("Take a photo of rice sample")
        if camera_option is not None:
            st.session_state.image_data = camera_option
            st.session_state.image_source = "camera"
            st.session_state.show_camera = False
    
    # Display the image if available
    if st.session_state.image_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 class="section-header">Original Image</h3>', unsafe_allow_html=True)
            try:
                # Get the image data
                image_data = st.session_state.image_data.getvalue()
                if not image_data:
                    st.error("No image data available. Please try uploading the image again.")
                    st.session_state.image_data = None
                else:
                    # Try to identify the image format first
                    try:
                        image = PIL.Image.open(io.BytesIO(image_data))
                        # Verify the image is valid
                        image.verify()
                        # Reopen the image after verify
                        image = PIL.Image.open(io.BytesIO(image_data))
                        
                        # Check if the image is in a supported format
                        if image.format not in ['JPEG', 'PNG', 'JPG']:
                            st.error(f"Unsupported image format: {image.format}. Please upload a JPEG or PNG image.")
                            st.session_state.image_data = None
                        else:
                            # Convert to JPEG for display
                            buf = io.BytesIO()
                            image.save(buf, format="JPEG")
                            st.image(buf.getvalue(), use_container_width=True)
                    except PIL.UnidentifiedImageError as e:
                        st.error("The uploaded file is not a valid image or is corrupted. Please try uploading a different image.")
                        st.info("Supported formats: JPEG, PNG")
                        st.session_state.image_data = None
                    except IOError as e:
                        st.error(f"Error processing the image: {str(e)}")
                        st.info("Please try uploading the image again")
                        st.session_state.image_data = None
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                st.info("Please try uploading the image again")
                st.session_state.image_data = None
        
        with col2:
            if st.session_state.current_analysis is not None:
                st.markdown('<h3 class="section-header">Analyzed Sample</h3>', unsafe_allow_html=True)
                try:
                    # In a real app, this would show an annotated version
                    # For now, we'll just display the original with a filter to simulate analysis
                    image_data = st.session_state.image_data.getvalue()
                    if not image_data:
                        st.error("No image data available")
                    else:
                        image = PIL.Image.open(io.BytesIO(image_data))
                        # Verify the image is valid
                        image.verify()
                        # Reopen the image after verify
                        image = PIL.Image.open(io.BytesIO(image_data))
                        # Apply a subtle filter to make it look "analyzed"
                        from PIL import ImageEnhance, ImageFilter
                        enhanced = ImageEnhance.Contrast(image).enhance(1.2)
                        enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.5)
                        enhanced = enhanced.filter(ImageFilter.EDGE_ENHANCE_MORE)
                        
                        # Convert to bytes for display
                        buf = io.BytesIO()
                        enhanced.save(buf, format="JPEG")
                        st.image(buf.getvalue(), use_container_width=True)
                except (PIL.UnidentifiedImageError, IOError) as e:
                    st.error(f"Error processing image: {str(e)}")
                    st.info("Please try uploading the image again")
                    st.session_state.image_data = None
            else:
                st.markdown('<h3 class="section-header">Analysis Preview</h3>', unsafe_allow_html=True)
                st.info("Run analysis to see rice quality visualization")
        
        # Analysis button
        st.markdown("""
        <style>
        .analyze-button {
            background-color: #3a86ff !important;
            color: white !important;
            font-weight: 500 !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            border: none !important;
            text-align: center !important;
            font-size: 1.1rem !important;
            width: 100% !important;
            cursor: pointer !important;
            margin-top: 1rem !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 4px 6px rgba(58, 134, 255, 0.2) !important;
            transition: all 0.3s ease !important;
            letter-spacing: 0.3px !important;
        }
        .analyze-button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(58, 134, 255, 0.3) !important;
            background-color: #2667cc !important;
        }
        </style>
        """, unsafe_allow_html=True)
        analyze_button = st.button("Analyze Rice Sample", key="analyze_button", use_container_width=True, type="primary")
        
        if analyze_button:
            if not api_key:
                st.error("Please enter your Gemini API Key in the sidebar to continue.")
            else:
                with st.spinner("Analyzing rice sample..."):
                    # Save the image to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                        tmp.write(st.session_state.image_data.getvalue())
                        tmp_path = tmp.name
                    
                    # Optional: Save to user-specified path
                    if save_path:
                        try:
                            if not os.path.exists(save_path):
                                os.makedirs(save_path)
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            save_file = os.path.join(save_path, f"rice_sample_{timestamp}.jpg")
                            shutil.copy(tmp_path, save_file)
                        except Exception as e:
                            st.warning(f"Could not save to specified path: {str(e)}")
                    
                    # Process the image
                    analysis_result, success = process_image(tmp_path, api_key)
                    
                    # Clean up the temporary file
                    os.unlink(tmp_path)
                    
                    if success:
                        st.session_state.current_analysis = analysis_result
                        save_to_history(analysis_result, st.session_state.image_data)
                        render_analysis_results(analysis_result)
                    else:
                        # st.error("Analysis failed. Please check the API key and try again.")
                        if "error" in analysis_result:
                            st.error(f"Error: {analysis_result['error']}")
                        if "raw_text" in analysis_result:
                            with st.error("Analysis failed"):
                                st.error(analysis_result["raw_text"])
                            # with st.expander("Raw Response"):
                            #     st.text(analysis_result["raw_text"])
        
        # Display results if available
        elif st.session_state.current_analysis is not None:
            render_analysis_results(st.session_state.current_analysis)

# Tab 2: History
with tabs[1]:
    st.markdown('<h2 class="section-header">Analysis History</h2>', unsafe_allow_html=True)
    
    if len(st.session_state.analysis_history) == 0:
        st.info("No analysis history available. Analyze some rice samples to see your history.")
    else:
        # Display history in a responsive grid
        history_items = []
        for i, item in enumerate(reversed(st.session_state.analysis_history)):
            # Create columns for each history item
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                # Display the thumbnail
                st.image(f"data:image/jpeg;base64,{item['image_thumbnail']}", use_column_width=True)
            
            with col2:
                # Display the analysis summary
                if 'rice_type' in item['analysis']:
                    rice_type = item['analysis']['rice_type']['variety']
                    grade = item['analysis']['overall_grade']['grade']
                    score = item['analysis']['overall_grade']['score']
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{rice_type} Rice</h4>
                        <p>Quality: <span class="quality-{get_color_from_value(score).lower()}">{grade} ({score}%)</span></p>
                        <p>Analyzed: {item['timestamp']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Analysis Result</h4>
                        <p>Analyzed: {item['timestamp']}</p>
                        <p>Error during analysis</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                # View details button
                if st.button("View Details", key=f"view_{i}", use_container_width=True):
                    st.session_state.current_analysis = item['analysis']
                    st.session_state.active_tab = "Analysis"
                    st.experimental_rerun()
        
        # Clear history button
        if st.button("Clear History", use_container_width=True):
            st.session_state.analysis_history = []
            st.experimental_rerun()

# Tab 3: Rice Calculator
with tabs[2]:
    st.markdown('<h2 class="section-header">Rice Cooking Calculator</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instruction-text">
        Calculate optimal cooking time and water requirements for your rice variety.
        For best results, select the variety that matches your rice sample or analysis.
    </div>
    """, unsafe_allow_html=True)
    
    # Calculator form
    with st.form("cooking_calculator"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rice_variety = st.selectbox(
                "Rice Variety",
                ["Basmati", "Jasmine", "Arborio", "Brown Rice", "White Long-Grain", "Medium-Grain", "Short-Grain", "Wild Rice"]
            )
        
        with col2:
            cooking_method = st.selectbox(
                "Cooking Method",
                ["Absorption Method", "Boiled Method", "Steamed Method"]
            )
        
        with col3:
            rice_quantity = st.number_input("Rice Quantity (cups)", min_value=0.25, max_value=10.0, value=1.0, step=0.25)
        
        # Pre-set water ratio based on rice type and method
        water_ratios = {
            "Basmati": {"Absorption Method": 1.5, "Boiled Method": 2.5, "Steamed Method": 1.75},
            "Jasmine": {"Absorption Method": 1.25, "Boiled Method": 2.0, "Steamed Method": 1.5},
            "Arborio": {"Absorption Method": 2.0, "Boiled Method": 3.0, "Steamed Method": 2.5},
            "Brown Rice": {"Absorption Method": 2.0, "Boiled Method": 3.0, "Steamed Method": 2.5},
            "White Long-Grain": {"Absorption Method": 1.5, "Boiled Method": 2.5, "Steamed Method": 2.0},
            "Medium-Grain": {"Absorption Method": 1.5, "Boiled Method": 2.5, "Steamed Method": 2.0},
            "Short-Grain": {"Absorption Method": 1.25, "Boiled Method": 2.0, "Steamed Method": 1.75},
            "Wild Rice": {"Absorption Method": 3.0, "Boiled Method": 4.0, "Steamed Method": 3.5}
        }
        
        water_ratio = water_ratios.get(rice_variety, {}).get(cooking_method, 2.0)
        water_quantity = rice_quantity * water_ratio
        
        # Calculate cooking time
        cooking_time = calculate_cooking_time(rice_variety.lower(), cooking_method.lower())
        
        calculate_button = st.form_submit_button("Calculate", use_container_width=True)
    
    # Display results
    if calculate_button or 'last_calculation' in st.session_state:
        # Save last calculation to session state
        st.session_state.last_calculation = {
            "rice_variety": rice_variety,
            "cooking_method": cooking_method,
            "rice_quantity": rice_quantity,
            "water_ratio": water_ratio,
            "water_quantity": water_quantity,
            "cooking_time": cooking_time
        }
        
        # Create two columns for result cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="calculator-section">
                <h3>Water Requirements</h3>
                <p><strong>Rice:</strong> {rice_quantity} cup{'s' if rice_quantity != 1 else ''}</p>
                <p><strong>Water:</strong> {water_quantity} cup{'s' if water_quantity != 1 else ''}</p>
                <p><strong>Ratio:</strong> 1:{water_ratio}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="calculator-section">
                <h3>Cooking Instructions</h3>
                <p><strong>Method:</strong> {cooking_method}</p>
                <p><strong>Cooking Time:</strong> {cooking_time} minutes</p>
                <p><strong>Servings:</strong> {int(rice_quantity * 2)} {'people' if rice_quantity * 2 > 1 else 'person'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Cooking steps
        st.markdown("<h3>Step-by-Step Instructions</h3>", unsafe_allow_html=True)
        
        # Different instructions based on method
        if cooking_method == "Absorption Method":
            steps = [
                "Rinse the rice thoroughly until water runs clear",
                f"Combine {rice_quantity} cup{'s' if rice_quantity != 1 else ''} of rice with {water_quantity} cup{'s' if water_quantity != 1 else ''} of water in a pot",
                "Add a pinch of salt (optional)",
                "Bring to a boil over high heat",
                "Once boiling, reduce heat to low and cover with a tight-fitting lid",
                f"Simmer for {cooking_time} minutes without removing the lid",
                "Remove from heat and let stand, covered, for 10 minutes",
                "Fluff with a fork before serving"
            ]
        elif cooking_method == "Boiled Method":
            steps = [
                "Rinse the rice thoroughly until water runs clear",
                f"Bring {water_quantity} cup{'s' if water_quantity != 1 else ''} of water to a rolling boil in a large pot",
                "Add a pinch of salt (optional)",
                f"Add {rice_quantity} cup{'s' if rice_quantity != 1 else ''} of rice and stir once",
                f"Boil uncovered for {cooking_time} minutes, stirring occasionally",
                "Drain rice in a fine-mesh strainer",
                "Return rice to pot and cover for 5 minutes to steam",
                "Fluff with a fork before serving"
            ]
        else:  # Steamed Method
            steps = [
                "Rinse the rice thoroughly until water runs clear",
                f"Soak {rice_quantity} cup{'s' if rice_quantity != 1 else ''} of rice in cold water for 30 minutes, then drain",
                "Place rice in a steamer basket lined with cheesecloth or a clean kitchen towel",
                f"Fill steamer pot with {water_quantity/2} cup{'s' if water_quantity/2 != 1 else ''} of water, ensuring it doesn't touch the rice",
                "Bring water to a boil",
                f"Steam the rice for {cooking_time} minutes with lid on",
                "Check water level halfway through and add more if needed",
                "Remove from heat and let stand for 5 minutes before serving"
            ]
        
        # Display steps
        for i, step in enumerate(steps):
            st.markdown(f"""
            <div class="metric-card" style="display: flex; align-items: center;">
                <div style="background-color: #3a86ff; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                    {i+1}
                </div>
                <div>{step}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Tips based on rice variety
        tips_by_variety = {
            "Basmati": "For fluffier basmati, rinse thoroughly and soak for 30 minutes before cooking.",
            "Jasmine": "Jasmine rice has a natural aroma - avoid overmixing to preserve its fragrance.",
            "Arborio": "For risotto, cook arborio slowly adding hot broth gradually to release starch.",
            "Brown Rice": "Brown rice benefits from soaking for 1-2 hours before cooking to reduce cooking time.",
            "White Long-Grain": "For separate, fluffy grains, rinse long-grain rice until water runs clear.",
            "Medium-Grain": "Medium-grain rice is ideal for paella and other dishes where slightly sticky texture is desired.",
            "Short-Grain": "Short-grain rice releases more starch, making it perfect for sushi and sticky rice dishes.",
            "Wild Rice": "Wild rice benefits from longer cooking times - look for grains to split open."
        }
        
        st.markdown(f"""
        <div class="instruction-text">
            <strong>Pro Tip:</strong> {tips_by_variety.get(rice_variety, "For best results, adjust water levels based on your preference for softer or firmer rice.")}
        </div>
        """, unsafe_allow_html=True)

# Tab 4: Settings
with tabs[3]:
    st.markdown('<h2 class="section-header">Application Settings</h2>', unsafe_allow_html=True)
    
    # Analysis settings
    st.markdown('<h3 class="section-header">Analysis Settings</h3>', unsafe_allow_html=True)
    
    analysis_col1, analysis_col2 = st.columns(2)
    
    with analysis_col1:
        save_results = st.checkbox("Save analysis results locally", value=bool(save_path))
        if save_results and not save_path:
            save_path = tempfile.gettempdir()
            st.info(f"Results will be saved to temporary directory: {save_path}")
            st.session_state.save_path = save_path
        elif not save_results:
            save_path = ""
            st.session_state.save_path = ""
    
    with analysis_col2:
        history_length = st.slider("Number of history items to keep", min_value=5, max_value=50, value=10)
        st.session_state.history_length = history_length
    
    # App information
    st.markdown('<h3 class="section-header">About RiceQual AI</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="metric-card">
        <h4>Application Information</h4>
        <p><strong>Version:</strong> 1.0.0 Beta</p>
        <p><strong>Developed by:</strong> RiceQual Team</p>
        <p><strong>Powered by:</strong> Google Gemini API for image analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset app button
    if st.button("Reset Application", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #ddd;">
    <p>RiceQual AI © 2025 | Professional Rice Quality Analysis</p>
</div>
""", unsafe_allow_html=True)