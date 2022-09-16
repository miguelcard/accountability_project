import React from 'react'
import '../../assets/styles/components/Home/howItsWorks.css'
import imagePlan from '../../assets/statics/images/NumberHeading.png'
import imageTrack from '../../assets/statics/images/NumberHeading2.png'
import imageAdjust from '../../assets/statics/images/NumberHeading3.png'
import imageRinse from '../../assets/statics/images/NumberHeading4.png'



const HowItWorks = () => {
    return (
        <div className="all-wraper">
            <div className="firt-content">
                <h1>How it works</h1>
                <p>create your profile in less than one minute (no long surveys!) an then:</p>
            </div>
            <div className="secont-content">
                <div className="row1">
                    <img src={imagePlan} alt="plan"/>
                    <p>Decide what habit you want to build or reduce and set a schedule.</p>
                </div>
                <div className="row2">
                    <img src={imageTrack} alt="Track"/>
                    <p>Track your progress daily with our easy-to-use interface.</p>
                </div>
                <div className="row3">
                    <img src={imageAdjust} alt="Adjust"/>
                    <p>Adjust your goals based on your performance and weekly check-ins with your accountability partner.</p>
                </div>
                <div className="row4">
                    <img src={imageRinse} alt="Rinse"/>
                    <p>The goal of the website is for you to accomplish long term goals, so keep checking in.</p>
                </div>
            </div>
        </div>
    )
}

export default HowItWorks
