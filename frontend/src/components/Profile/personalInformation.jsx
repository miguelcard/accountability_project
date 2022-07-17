import React from 'react'
import ModalPhoto from './modalPhoto';
import { Button } from 'reactstrap'
import '../../assets/styles/components/Profile/index.css'
import pencil from '../../assets/statics/images/pencil.png'
import ModalAboutMe from './modalAboutMe';
import Loading from '../LoadingAndError/loading';



const PersonalInformation = ({
  userName,
  updatedUserPhoto,
  userPhoto,
  defaultPhoto,
  stateModal,
  openModal,
  openModalAbout,
  stateModalAbout,
  updatedAboutMe,
  aboutMe,
  fetching,
  token
}) => {

  if (fetching) return <Loading/>

  return (
    <>
      <div className="personal-information">
        <h1 id="personal-name">Hey {userName}</h1>
        <h2 id="complete-profile">complete my profile</h2>
        <div className="profile-photo">
          <img
            src={
              updatedUserPhoto
                ? `${updatedUserPhoto}`
                : userPhoto
                ? `${userPhoto}`
                : defaultPhoto
            }
            alt="profilePhoto"
            id="photo"
          />
          <Button  onClick={openModal} id="btn-pencil">
            {
              updatedUserPhoto
                ? <img src={pencil} alt="pencil"/>
                : userPhoto
                ? <img src={pencil} alt="pencil"/>
                : <p>Add photo</p>
            }
          </Button>
          <ModalPhoto
            token={token}
            isOpen={stateModal}
            openModal={openModal}
          />
        </div>
        <div className="about-me">
          <div className="content-about-me">
            <h2>About Me...</h2>
            {
              updatedAboutMe
                ? <p>{updatedAboutMe}</p>
                : aboutMe
                ? <p>{aboutMe}</p>
                : <p></p>
            }
          </div>
          <button id="about-pencil" onClick={openModalAbout}><img src={pencil} alt="pencil"/></button>
          <ModalAboutMe
            token={token}
            isOpen={stateModalAbout}
            openModal={openModalAbout}
          />
        </div>
      </div>
    </>
  );
};

export default PersonalInformation
