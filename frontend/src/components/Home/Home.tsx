import React from 'react'
import {Link} from 'react-router-dom'
import { useHistory } from "react-router-dom";

import LandingHeader from '../Header/LandingHeader'
import '../../assets/styles/components/Home/index.css'

const Home: React.FC = () => {

    let history = useHistory();

    const eventUp = () => {
        history.push('/register');
    }

    return (
        <>
            <div className="content-main">
                <div className="content-Header">
                    <LandingHeader/>
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
                        </div>
                        <div className="logo-info">
                        </div>
                    </div>
                </div>
                {/*  How it works and Frequently asked questions are just nice to have things at the end */}
                {/* <div> */}
                    {/* this is a "nice" component but lets just leave it out for now */}
                    {/* <div className="all-content-work">
                        <HowItWorks/>
                    </div>
                </div> */}
                {/* <div className="asked-questions">
                    <FrequentlyAsked/>
                </div> */}
                {/* FooterHome would go here */}
            </div>
        </>
    )
}

export default Home
