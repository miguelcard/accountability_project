import React from 'react'
import '../../assets/styles/components/Home/getAPartner.css'
import logoFearless from '../../assets/statics/images/logoFearless.png'
import airbnbLogo from '../../assets/statics/images/AirbnbLogo.png'
import bookMyShow from '../../assets/statics/images/Group.png'


const GetAPartner = () => {
    return (
        <>
        <div className="all-content-get-partner">
            <div className="content-left">
                <div className="why-a-partner">
                    <h1>Why should I get a partner?</h1>
                    <p>Having an accountability partner is a not so common method of unleashing your full potential. Here’s what other people have to say about having one. </p>
                </div>
                <div className="fearless">
                    <img src={logoFearless} alt="logoFearless"/>
                    <div className="content-fearless">
                        <p id="first-p">When you commit to someone that you will do it, <b>stretches your probability to 65%</b>. Moreover, when you create a specific accountability appointment with a person you are committed to, <b>the odds are in your favor: 95%.</b></p>
                        <h3><b>Gustavo Razzetti</b></h3>
                        <p id="second-p">Founder, Fearless Culture</p>
                    </div>
                </div>
            </div>
            <div className="content-right">
                <div className="testimonial-1">
                    <img src={airbnbLogo} alt="airbnb logo"/>
                    <div className="content-fearless">
                        <p id="first-p">I used landify and created a landing page for my startup within a week. The Landify UI Kit is simple and highly intuitive, so anyone can use it.</p>
                        <h3><b>Jane Cooper</b></h3>
                        <p id="second-p">CEO, Airbnb</p>
                    </div>
                </div>
                <div className="testimonial-2">
                    <img src={bookMyShow} alt="airbnb logo"/>
                    <div className="content-fearless">
                        <p id="first-p">Landify saved our time in designing my company page.</p>
                        <h3><b>Kristin Watson</b></h3>
                        <p id="second-p">Co-Founder, BookMyShow</p>
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}

export default GetAPartner
