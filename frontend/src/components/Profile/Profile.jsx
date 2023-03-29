import React, { useState } from 'react'
import {connect, useDispatch} from 'react-redux'
import { useHistory } from "react-router-dom";
import { logoutAction } from '../../redux/loginDucks';
import '../../assets/styles/components/Profile/index.css'
import profilePhoto from '../../assets/statics/images/Group2334.png'
import PersonalInformation from './PersonalInformation';


const TOTAL_LOGOUT_SUCCESS = 'TOTAL_LOGOUT_SUCCESS'


function Profile({ user, userUpdate, logoutAction, fetching }) {
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


  //  THIS IS ALL THE PROFILE LAYOUT, INCLUDING HEADERS AND FOOTERS IS THIS THE RIGHT PLACE FOR IT?, I ALSO DONT THINK THE HEADERS AND FOOTERS SHOULD BE DONE THIS WAY, RATHER TOGETHER IN A MORE REUSABLE FASHION
  // SHOULNT THE PROFILE PART BE IN THE profileView.jsx file in the views folder?
  return (
    <>
      {/* <HeaderProfile logout={logout} /> */}
      <button  onClick={logout}>Logout</button>

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