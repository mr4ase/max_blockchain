import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from 'react-bootstrap';
import Transaction from './Transaction';
import { API_BASE_URL, SECONDS_JS } from '../config';

const POLL_INTERVAL = 10 * SECONDS_JS;

function TransactionPool() {
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [fetchError, setFetchError] = useState('');
  const [miningError, setMiningError] = useState('');

  const fetchTransactions = () => {
    fetch(`${API_BASE_URL}/transaction-pool`)
      .then(async response => {
        const json = await response.json();
        if (!response.ok) {
          throw new Error(json.error || 'Transaction-pool fetching error!');
        }
        return json;

      })
      .then(json => {
        console.log('transactions json', json);
        setTransactions(json);
        setFetchError('');
      })
      .catch(error => {
        setFetchError(error.message);
      });
  }

  useEffect(() => {
    fetchTransactions();

    const intervalId = setInterval(fetchTransactions, POLL_INTERVAL);

    return () => clearInterval(intervalId);
  }, []);

  const fetchMineBlock = () => {
    setMiningError('');
    fetch(`${API_BASE_URL}/blockchain/mine`)
      .then( async response => {
        const json = await response.json();
        if (!response.ok) {
          throw new Error(json.error || 'Block mining failed');
        }

        return json;

      })
      .then(() => {
          navigate('/blockchain');
      })
      .catch(error => {
        setMiningError(error.message);
      });
  }

  return (
    <div className="TransactionPool">
      <Link to="/">Home</Link>
      <hr />
      <h3>Transaction Pool</h3>
      <div>
        {
          transactions.map(transaction => (
            <div key={transaction.id}>
              <hr />
              <Transaction transaction={transaction} />
            </div>
          ))
        }
      </div>
      <hr />
      {transactions.length === 0 && (
        <div>
          No pending transactions.
        </div>
      )}      
      <Button
        variant="danger"
        onClick={fetchMineBlock}
        disabled={transactions.length === 0}
      >
        Mine a block of these transactions
      </Button>

      {fetchError &&  (
          <div className='text-danger'>
            {fetchError}
          </div>
      )}
      {miningError &&  (
          <div className='text-danger'>
            {miningError}
          </div>
      )}
    </div>
  )
}

export default TransactionPool;
