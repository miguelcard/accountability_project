import React, { useState } from 'react'
import {connect, useDispatch} from 'react-redux'
import { useHistory } from "react-router-dom";
import { logoutAction } from '../../redux/loginDucks'
import FooterHome from '../Home/footerHome';
import HeaderProfile from './headerProfile';
import '../../assets/styles/components/Profile/index.css'
import profilePhoto from '../../assets/statics/images/Group2334.png'
import PersonalInformation from './personalInformation';
import Information from './information';
import PartnerPreference from './partnerPreference';
import Score from './score';


const TOTAL_LOGOUT_SUCCESS = 'TOTAL_LOGOUT_SUCCESS'


function Profile({ user, userUpdate, logoutAction, fetching, languageList }) {
  const history = useHistory();
  const dispatch = useDispatch();
  const [stateModal, setStateModal] = useState({ open: false });
  const [stateModalAbout, setStateModalAbout] = useState({ open: false });

  const openModal = () => {
    setStateModal({ open: !stateModal.open });
  };

  const openModalAbout = () => {
    setStateModalAbout({ open: !stateModalAbout.open });
  };

  const logout = async () => {
    logoutAction(user.authentication.token);
    dispatch({
      type: TOTAL_LOGOUT_SUCCESS,
    });
    localStorage.clear();
    history.push("/login");
  };

  return (
    <>
      <HeaderProfile logout={logout} />
      <div className="content-profile">
        <PersonalInformation
          token={user.authentication.token}
          userName={user.user.username}
          updatedUserPhoto={userUpdate.profile_photo}
          updatedAboutMe={userUpdate.about}
          aboutMe={user.user.about}
          userPhoto={user.user.profile_photo}
          defaultPhoto={profilePhoto}
          stateModal={stateModal.open}
          stateModalAbout={stateModalAbout.open}
          openModal={openModal}
          openModalAbout={openModalAbout}
          fetching={fetching}
        />
        <div className="information">
          <Information
            token={user.authentication.token}
            userInfo={user.user}
            userInfoUpdated={userUpdate}
            languageList={languageList}
          />
        </div>
        <div className="partner-preferences">
          <PartnerPreference />
        </div>
        <div className="your-score">
          <Score />
        </div>
      </div>
      <div className="footer">
        <FooterHome />
      </div>
    </>
  );
}

const mapStateToProps = (state) => {
  return {
    user: state.dataLogin.list,
    userUpdate: state.dataLogin.updatedList,
    fetching: state.dataLogin.fetching,
    languageList: state.dataLogin.languageList
  }
}

export default connect(mapStateToProps, { logoutAction })(Profile);