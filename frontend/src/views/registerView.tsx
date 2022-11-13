import React from 'react'
import HeaderLogin from '../components/Register/HeaderLogin'
import line from '../assets/statics/images/line.png'
import line2 from '../assets/statics/images/line2.png'
import Register from '../components/Register/Register'
import logoDown from '../assets/statics/images/girl-doing-yoga-2194219-0.png'
import '../assets/styles/components/Register/index.css'


const RegisterView: React.FC = () => {
    return (
        <>
            <div className="header-login">
                <HeaderLogin/>
            </div>
            <div className="wraper-register">
                <div className="container-register">
                    <div className="tittle-register">
                        <h1>Lets get you started.</h1>
                    </div>
                    <div className="register">
                        <div className="stn-2">
                            <h2>Its free and easy!</h2>
                            <img src={line2} alt='line' id='img-2'/>
                            <Register/>
                        </div>
                        <div className="stn-1">
                            <h2>Did you Know...</h2>
                            <img src={line} alt='line' id='img-1'/>
                            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi fermentum consequat mattis.. </p>
                            <button type="submit" className="btn btn-primary">Know more...</button>
                            <img src={logoDown} alt='logo' id='img-2'/>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default RegisterView
