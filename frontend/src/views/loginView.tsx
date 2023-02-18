import React from 'react'
import Login from '../components/Register/Login'
import '../assets/styles/components/Login/index.css'
// import HeaderLogin from '../components/Register/HeaderLogin'
// import logoDown from '../assets/statics/images/problem-solving-2194252-0.png'

const LoginView:React.FC = () => {
    return (
        <>
            <div className="header-login">
                {/* <HeaderLogin/> */}
                    the header login was here, not anymore
            </div>
            <div className="wraper-login">
                <div className="container-login">
                    <div className="tittle-login">
                        <h1>Glad to see you back.</h1>
                    </div>
                    <div className="login">
                        <div className="section-1">
                            <h2>welcome back to Find Our Tribe</h2>
                            {/* <img src={line} alt='line' id='img-1'/> */}
                            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi fermentum consequat mattis.. </p>
                            {/* <img src={logoDown} alt='logo' id='img-2'/> */}
                        </div>
                        <div className="section-2">
                            <h2>Sign In</h2>
                            {/* <img src={line2} alt='line' id='img-2'/> */}
                            <Login/>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default LoginView
