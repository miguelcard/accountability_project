import React from 'react'
import { Link } from 'react-router-dom';
import HeaderTest from '../components/Header/HeaderTest'
import ImagesSection from '../components/Home/ImagesSection'
import '../assets/styles/container/Home.css'

function Home(props) {
    return (
        <>
            <HeaderTest></HeaderTest>
            <section className="all-content">
                <section className="section-head">
                    <section className="section-3d">
                        <div className="section-img-vector1">
                            <ImagesSection/>
                            <div className="section-img-vector2">
                                <div className="img-vector2"></div>
                            </div>
                        </div>
                    <div className="section-info">
                            <h1 className="title">Need Motivation?</h1>
                            <h2 className="title">Need a Partner?</h2>
                            <p id="p1">Achive your Goals with an</p>
                            <p id="p2">Accountability Partner</p>
                            <div className="all-buttons-info">
                                <Link to="#login" id="btn-info1"><p>What is to be an Accountability Partner</p></Link>
                                <Link to="/register" id="btn-info2"><p>Get your Accountability Partner</p></Link>
                            </div>
                        </div>
                    </section>
                </section>
                <section>
                    <h2>asodncañsdlkncañsdkncañsdcnadcadcadc</h2>
                    <h2>asodncañsdlkncañsdkncañsdcnadcadcadc</h2>
                    <h2>asodncañsdlkncañsdkncañsdcnadcadcadc</h2>
                    <h2>asodncañsdlkncañsdkncañsdcnadcadcadc</h2>
                    <h2>asodncañsdlkncañsdkncañsdcnadcadcadc</h2>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                    <p>asodncañsdlkncañsdkncañsdcnadcadcadc</p>
                </section>
            </section>
        </>
    )
}

export default Home
