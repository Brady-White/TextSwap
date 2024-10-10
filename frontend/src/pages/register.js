import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [verificationLink, setVerificationLink] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate(); // Initialize the navigate hook

    const handleRegister = async (e) => {
        e.preventDefault(); // Prevent the default form submission
        try {
            // Send a POST request to the Flask backend
            const response = await axios.post('http://localhost:5000/register', {
                email: email,
                password: password,
            });
            // Assuming the response contains a verification link
            setVerificationLink(response.data.message);
            setError(''); // Clear any previous error messages
        } catch (error) {
            // Handle errors by setting the error state
            setError(error.response?.data?.error || 'Registration failed');
            setVerificationLink(''); // Clear verification link on error
        }
    };

    const handleOkClick = () => {
        navigate('/'); // Navigate to the login page
    };

    return (
        <div>
            <h2>Register</h2>
            <form onSubmit={handleRegister}>
                <input 
                    type="email" 
                    placeholder="Email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                    required 
                />
                <input 
                    type="password" 
                    placeholder="Password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    required 
                />
                <button type="submit">Register</button>
            </form>

            {verificationLink && (
                <div>
                    <p>Registration successful! Please check your email inbox for a verification link in order to signin.</p>
                    <button onClick={handleOkClick}>OK</button> {/* Add click handler for OK button */}
                </div>
            )}

            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default Register;
