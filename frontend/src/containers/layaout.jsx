import React from 'react'
import FooterHome from '../components/Home/footerHome'
import HeaderProfile from '../components/Profile/headerProfile'

const Layaout = ({children}) => {
    return (
        <div className="layout">
            <HeaderProfile/>
            {children}
            <div className="footer">
                <FooterHome />
            </div>
        </div>
    )
}

export default Layaout
