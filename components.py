# components.py - For handling JavaScript geolocation
import streamlit as st
import streamlit.components.v1 as components

def get_geolocation():
    """Create a component to get geolocation"""
    
    geolocation_js = """
    <script>
    // Function to get geolocation
    function getGeolocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation not supported'));
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: position.timestamp
                    });
                },
                (error) => {
                    reject(error);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }
    
    // Execute and send message to parent
    getGeolocation()
        .then(position => {
            window.parent.postMessage({
                type: 'geolocation',
                data: position
            }, '*');
        })
        .catch(error => {
            window.parent.postMessage({
                type: 'geolocation_error',
                error: error.message
            }, '*');
        });
    </script>
    """
    
    # Create an iframe to run the JavaScript
    components.html(geolocation_js, height=0)
