import React from 'react';
import {
  Navbar,
  NavbarBrand,
  NavbarText
} from 'reactstrap';
import logotype from '../../assets/statics/images/logotype.png'
import '../../assets/styles/components/Login/headerLoginStyle.css'





const HeaderLogin = (props) => {
  
    return (
      <>
        <Navbar className="total-nav" light expand="lg">
          <NavbarBrand href="/" className="logotipeLogin">
            <img src={logotype} alt="logo" />
          </NavbarBrand>
          <NavbarText className="ml-auto" id="secont-item">
            FAQ
          </NavbarText>
        </Navbar>
      </>
    );
}

export default HeaderLogin
