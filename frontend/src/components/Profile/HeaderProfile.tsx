import React, {useState} from 'react'
import {
    Collapse,
    Navbar,
    NavbarToggler,
    NavbarBrand,  // really? "Brand"? this is called LOGO 
    Nav,
    NavItem,
    NavLink,
} from 'reactstrap';
// import logotype from '../../assets/statics/images/logotype.png'
import '../../assets/styles/components/Profile/headerProfile.css'

const HeaderProfile: React.FC<any> = (props) => {              // this name "Header Profile" is not intuitive at all, this is just a header when the user is logged in, it would also not belong to this profile folder
    const [isOpen, setIsOpen] = useState<boolean>(false);

    const toggle = () => setIsOpen(!isOpen);


    return (
        <>
            <Navbar light expand="lg" className="position-fixed" id="all-content-nav">
                {/* <NavbarBrand href="/" className="navbar-logotype"><img src={logotype} alt="logo"/></NavbarBrand> */}
                <NavbarToggler onClick={toggle} />
                <Collapse isOpen={isOpen} navbar>
                    <Nav className="ml-auto" navbar id="nav">
                        <NavItem className="item-1">
                            <NavLink href="/dashboard" id="link">Dashboard</NavLink>
                        </NavItem>
                        <NavItem className="item-2">
                            <NavLink href="#" id="link">Scoreboard</NavLink>
                        </NavItem>
                        <NavItem className="item-3">
                            <NavLink href="#" id="link">My Partners</NavLink>
                        </NavItem>
                        <NavItem className="item-4">
                            <NavLink href="/profile" id="link">Profile</NavLink>
                        </NavItem>
                    </Nav>
                    <button className="btn btn-primary" id="profile-btn" onClick={props.logout}>Logout</button>
                </Collapse>
            </Navbar>
        </>
    );
}

export default HeaderProfile
