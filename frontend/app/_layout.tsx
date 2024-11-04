import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from './screens/login';
import RegisterScreen from './screens/register';
import DashboardScreen from './screens/dashboard';
import EditListingScreen from './screens/editlisting';
import { UserProvider } from './screens/UserContext';

const Stack = createStackNavigator();

export default function App() {
    return (
        <UserProvider>
            <NavigationContainer independent={true}>
                <Stack.Navigator initialRouteName="Login">
                    <Stack.Screen name="Login" component={LoginScreen} />
                    <Stack.Screen name="Register" component={RegisterScreen} />
                    <Stack.Screen name="Dashboard" component={DashboardScreen} />
                    <Stack.Screen name="Edit Listing" component={EditListingScreen} />
                </Stack.Navigator>
            </NavigationContainer>
        </UserProvider>
    );
}
