import React from 'react'
import HeaderProfile from '../components/Profile/headerProfile'

const Layaout = ({ children }) => {
    return (
        <div className="layout">
            <HeaderProfile />
            {children}
            {/* the space between these 2 is quite badly formatted */}
            {/* FooterComponent would go here */}
        </div>
    )
}

export default Layaout
