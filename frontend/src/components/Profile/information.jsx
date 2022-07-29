import React, { useState } from 'react'
import pencil from '../../assets/statics/images/pencil.png'
import { searchingLanguage } from '../../redux/loginDucks'
import ModalInformation from './modalInformation'



const Information = ({ token, userInfo, userInfoUpdated, languageList }) => {

    const [stateModalInformation, setStateModalInformation] = useState({open: false})
    const languages = userInfo.languages.map(item => item.name)

    const openModalInfo = () => {
        setStateModalInformation({open: !stateModalInformation.open})
    }

    const updatedLanguage = () => {
        if (userInfoUpdated.languages) {
            let convertToString = userInfoUpdated.languages.toString()
            let convertToNum = parseInt(convertToString)
            const res = searchingLanguage(languageList, convertToNum)
            return res.toString()
        }
    }

    return (
        <div className="square-info">
            <div className="tittle-info">
                <h2>Personal Information</h2>
            </div>
            <div className="information-list">
                <div className="info-row-1">
                    <p>First Name: { userInfoUpdated.name? <b>{userInfoUpdated.name}</b>: userInfo.name? <b>{userInfo.name}</b>: <b>None</b>}</p>
                    <p>Last Name: { userInfoUpdated.last_name? <b>{userInfoUpdated.last_name}</b>: userInfo.last_name? <b>{userInfo.last_name}</b>: <b>None</b>}</p>
                    <p>Bithday: { userInfoUpdated.birthdate? <b>{userInfoUpdated.birthdate}</b>: userInfo.birthdate? <b>{userInfo.birthdate}</b>: <b>None</b>}</p>
                    <p>{userInfo.age? <>Age(s): <b>{userInfo.age}</b></>: <>Age(s): <b>None</b></>}</p>
                </div>
                <div className="info-row-2">
                    <p>Language(s): {userInfoUpdated.languages? <b>{updatedLanguage()}</b>: userInfo.languages.map(item => item.id) >= 1? <b>{languages.toString()}</b>: <b>None</b>}</p>
                    <p>Goals & Habits:</p>
                    <p>Gender: </p>
                </div>
            </div>
            <button id="personal-pencil" onClick={openModalInfo}><img src={pencil} alt="pencil"/></button>
            <ModalInformation
                token={token}
                isOpen={stateModalInformation.open}
                openModal={openModalInfo}
            />
        </div>
    )
}

export default Information
