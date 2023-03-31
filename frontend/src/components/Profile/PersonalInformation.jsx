import React from 'react'
import ModalPhoto from './ModalPhoto';
import ModalAboutMe from './ModalAboutMe';
import Loading from '../LoadingAndError/Loading';



const PersonalInformation = ({
  userName,
  updatedUserPhoto,
  userPhoto,
  defaultPhoto,
  updatedAboutMe,
  aboutMe,
  fetching,
  token
}) => {

  if (fetching) return <Loading />

  return (
    <>
      <div>
        <h1>Hey {userName}</h1>
        <h2>complete my profile</h2>
        <div>
          <img
            src={
              updatedUserPhoto
                ? `${updatedUserPhoto}`
                : userPhoto
                  ? `${userPhoto}`
                  : defaultPhoto
            }
            alt="profilePhoto"
          />
          <ModalPhoto
            token={token}
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
          <ModalAboutMe
            token={token} // do we have to pass this token to all components?? this can not be right
          />
        </div>
      </div>
    </>
  );
};

export default PersonalInformation
