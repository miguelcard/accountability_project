import React from 'react'
import { Link, useHistory } from 'react-router-dom'
import '../../assets/styles/components/Home/frequentlyAsked.css'
import icon1 from '../../assets/statics/images/IconBox1.png'
import iconOthersBox from '../../assets/statics/images/iconPlusBox.png'


const FrequentlyAsked = () => {

    const history = useHistory()

    const createAccount = () => {
        history.push('/register')
    }

    return (
        <div className="content-frequently-asked">
            <div className="cnt1">
                <h1 id="tittle1">Frequently Asked Questions</h1>
                <div className="total-box">
                    <div className="box-left">
                        <div className="box1">
                            <img src={icon1} alt="icon"/>
                            <h2>what is an accountability partner?</h2>
                            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi fermentum consequat mattis. </p>
                        </div>
                        <div id="box2"><Link to="#"/>
                            <img src={iconOthersBox} alt="icon"/>
                            <h2>Should I just go to WhatsApp or Facebook to find one?</h2>
                        </div>
                    </div>
                    <div className="box-right">
                        <div id="box3"><Link to="#"/>
                            <img src={iconOthersBox} alt="icon"/>
                            <h2>What is the price of using the website?</h2>
                        </div>
                        <div id="box4"><Link to="#"/>
                            <img src={iconOthersBox} alt="icon"/>
                            <h2>How long does it take to get matched?</h2>
                        </div>
                        <div id="box5"><Link to="#"/>
                            <img src={iconOthersBox} alt="icon"/>
                            <h2>Can I chat with my accountability partner?</h2>
                        </div>
                    </div>
                </div>
            </div>
            <div className="cnt2">
                <h1 className="tittle2">Still Reading this? Lets Get You Started!</h1>
                <button onClick={createAccount} className="btn btn-primary" id="button-cnt2">Create an Account</button>
            </div>
        </div>
    )
}

export default FrequentlyAsked
