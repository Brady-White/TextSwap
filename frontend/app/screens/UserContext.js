import React, { createContext, useState, useContext } from 'react';

// Create the User Context
const UserContext = createContext();

// Create a custom hook to easily use the User Context
export const useUser = () => useContext(UserContext);

// Context provider component
export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    );
};
