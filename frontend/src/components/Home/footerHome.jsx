import React from 'react'
import { Link } from 'react-router-dom'
import '../../assets/styles/components/Home/footerHome.css'

const FooterHome = () => {
    return (
        <div className="content-footer">
            <div className="principal-box">
                <h3>Content...</h3>
                <p>Got a questions? Reach us at <Link to="#" id="support">support@findourtribe.com</Link></p>
            </div>
            <div className="menu-1">
                <h3>MENU</h3>
                <ul>
                    <li><Link to="/" id="lk"><p>Home</p></Link></li>
                    <li><Link to="#" id="lk"><p>About</p></Link></li>
                    <li><Link to="#" id="lk"><p id="long">Contact Us</p></Link></li>
                    <li><Link to="#" id="lk"><p>FAQ</p></Link></li>
                </ul>
            </div>
            <div className="menu-2">
                <h3>Social</h3>
                <ul>
                    <li><Link to="#" id="lk"><p>Twitter</p></Link></li>
                    <li><Link to="#" id="lk"><p>Instagram</p></Link></li>
                    <li><Link to="#" id="lk"><p>Facebook</p></Link></li>
                </ul>
            </div>
            <div className="menu-3">
                <h3>Legal</h3>
                <ul>
                    <li><Link to="#" id="lk"><p id="long">Terms of Use</p></Link></li>
                    <li><Link to="#" id="lk"><p id="long">Privace policy</p></Link></li>
                    <li><Link to="#" id="lk"><p id="long">Legal Notice</p></Link></li>
                </ul>
            </div>
        </div>
    )
}

export default FooterHome
