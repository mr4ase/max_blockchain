import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FormGroup, FormControl, Button } from 'react-bootstrap';
import { API_BASE_URL } from '../config';

function ConductTransaction() {
  const navigate = useNavigate();
  const [amount, setAmount] = useState(0);
  const [recipient, setRecipient] = useState('');
  const [knownAddresses, setKnownAddresses] = useState([]);
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API_BASE_URL}/known-addresses`)
      .then(response => response.json())
      .then(json => setKnownAddresses(json));
  }, []);

  const updateRecipient = event => {
    setRecipient(event.target.value);
  }

  const updateAmount = event => {
    setAmount(Number(event.target.value));
  }

  const getErrorMessage = json => {
    if (typeof json.details === 'string') {
      return json.details;
    }

    if (Array.isArray(json.details) && json.details.length > 0) {
      return json.details[0].msg;
    }

    return json.error || 'Transaction failed';
  };

  const submitTransaction = () => {
    setError('');
    fetch(`${API_BASE_URL}/blockchain/transaction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        recipient_address: recipient, 
        amount 
      })
    }).then( async response => {
      const json = await response.json();
      
      if (!response.ok) {
        throw new Error(getErrorMessage(json));
      }

      return json;

      })
      .then(json => {
        console.log('submitTransaction json', json);
        navigate('/transaction-pool');
      })
      .catch(error => {
        setError(error.message);
      });
  }

  return (
    <div className="ConductTransaction">
      <Link to="/">Home</Link>
      <hr />
      <h3>Conduct a Transaction</h3>
      <br />
      <FormGroup>
        <FormControl
          input="text"
          placeholder="recipient"
          value={recipient}
          onChange={updateRecipient}
        />
      </FormGroup>
      <FormGroup>
        <FormControl
          input="number"
          placeholder="amount"
          value={amount}
          onChange={updateAmount}
        />
      </FormGroup>
      <div>
        <Button
          variant="danger"
          onClick={submitTransaction}
        >
          Submit
        </Button>
        {error &&  (
          <div className='text-danger'>
            {error}
          </div>
        )}
      </div>
      <br />
      <h4>Known Addresses</h4>
      <div>
        {
          knownAddresses.map((knownAddress, i) => (
            <span key={knownAddress}>
              <u>{knownAddress}</u>{i !== knownAddresses.length - 1 ? ', ' : ''}
            </span>
          ))
        }
      </div>
    </div>
  )
}

export default ConductTransaction;
