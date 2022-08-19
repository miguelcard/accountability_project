import React from 'react'
import FooterHome from '../components/Home/FooterHome'
import HeaderProfile from '../components/Profile/headerProfile'

const Layaout = ({ children }) => {
    return (
        <div className="layout">
            <HeaderProfile />
            {children}
            {/* the space between these 2 is quite badly formatted */}
            <FooterHome />
        </div>
    )
}

export default Layaout
