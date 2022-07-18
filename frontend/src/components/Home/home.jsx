import React from 'react'
import {Link} from 'react-router-dom'
import { useHistory } from "react-router-dom";

import Header from '../Header/header'
import '../../assets/styles/components/Home/index.css'
import '../../assets/styles/components/Home/responsiveDesing.css'
import logoCircle2 from '../../assets/statics/images/TurquoiseCircle.png'
import logoCircle1 from '../../assets/statics/images/OrangeCircle.png'
import HowItsWork from './howItsWork';
import imageHuman from '../../assets/statics/images/super-hero-on-duty-in-business-leader-concept-2194246-0.png'
import GetAPartner from './getAPartner';
import FrequentlyAsked from './frequentlyAsked';
import FooterHome from './footerHome';

const Home = () => {

    let history = useHistory();

    const eventUp = () => {
        history.push('/register');
    }

    return (
        <>
            <div className="content-main">
                <div className="content-Header">
                    <Header/>
                    <div className="container-header">
                        <div className="info">
                            <div className="tittle">
                                <h1 id="t1">Where accountability</h1>
                                <h1 id="t1">meets partner</h1>
                            </div>
                            <p id="phara">Meet Find Our Tribe. The best website to get motivated, build healthy habits, and find an accountability partner</p>
                            <button onClick={eventUp} type="button" className="btn btn-primary" id="btn-getStart">Get Started</button>
                            <div className="signIn">
                                <p>Or, just <Link to="/login" className="link-signin">SignIn</Link></p>
                            </div>
                            <img src={logoCircle1} alt="cirlce1"/>
                        </div>
                        <div className="logo-info">
                            <img src={logoCircle2} alt="circle2"/>
                        </div>
                    </div>
                </div>
                <div className="how-its-work">
                    <div className="all-content-work">
                        <HowItsWork/>
                    </div>
                </div>
                <div className="getApartner">
                    <img src={imageHuman} alt="imageHuman"/>
                    <GetAPartner/>
                </div>
                <div className="asked-questions">
                    <FrequentlyAsked/>
                </div>
                <div className="footer">
                    <FooterHome/>
                </div>
            </div>
        </>
    )
}

export default Home
