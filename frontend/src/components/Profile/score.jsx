import React from 'react'

const Score = () => {
    return (
        <div className="total-score">
            <div className="score">
                <h2>Your Accountability Score</h2>
                <div>
                    <h3>stars...</h3>
                </div>
            </div>
            <div className="tips">
                <h3>Tips to increase your Score:</h3>
                <ul>
                    <li>Complete your profile</li>
                    <li>Match with an Accountability partner</li>
                    <li>Join a Group</li>
                    <li>Attend a weekly review with your partner</li>
                </ul>
            </div>
        </div>
    )
}

export default Score
