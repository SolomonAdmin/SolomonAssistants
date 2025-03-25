exports.main = async (context, sendResponse) => {
    const accessToken = process.env.HUBSPOT_ACCESS_TOKEN;
    const companyId = context.object.objectId;
    console.log(`Starting process for Company ID: ${companyId}`);
  
    const counters = {
      totalCreditsAvailable: { count: 0, matches: [] },
      extendedPlacementCredits: { count: 0, matches: [] },
      totalCreditsPurchased: { count: 0, matches: [] },
      dealCreditsAvailable: { count: 0, matches: [] },
      dealCreditsPurchased: { count: 0, matches: [] }
    };
  
    const uniqueValues = {
      pipelines: new Set(),
      stages: new Set(),
      products: new Set()
    };
  
    if (!companyId || isNaN(companyId)) {
      console.error('Invalid or missing Company ID');
      sendResponse({
        message: 'Error: Invalid or missing Company ID',
        error: 'Company ID must be numeric and valid'
      });
      return;
    }
  
    const fetchBatchDealAssociations = async (ticketIds) => {
      try {
        const response = await fetch(
          `https://api.hubapi.com/crm/v3/associations/tickets/deals/batch/read`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              inputs: ticketIds.map(id => ({ id }))
            })
          }
        );
  
        if (!response.ok) {
          throw new Error(`Error fetching deal associations: ${await response.text()}`);
        }
  
        const data = await response.json();
        const ticketDealMap = {};
        
        data.results.forEach(result => {
          if (result.to && result.to.length > 0) {
            ticketDealMap[result.from.id] = result.to[0].id;
          }
        });
  
        return ticketDealMap;
      } catch (error) {
        console.error('Error in batch association:', error);
        return {};
      }
    };
  
    const processTicketBatch = async (tickets) => {
      const ticketDealMap = await fetchBatchDealAssociations(tickets.map(t => t.id));
      const dealUpdates = new Map();
  
      tickets.forEach(ticket => {
        const properties = ticket.properties || {};
        const pipeline = properties['hs_pipeline']?.toString() || 'N/A';
        const pipelineStage = properties['hs_pipeline_stage']?.toString() || 'N/A';
        const productId = properties['product_id_']?.toString() || 'N/A';
  
        uniqueValues.pipelines.add(pipeline);
        uniqueValues.stages.add(pipelineStage);
        uniqueValues.products.add(productId);
  
        // Original company-level counters
        if (pipelineStage === '61272329' && ['3652447404', '3299780235'].includes(productId)) {
          counters.totalCreditsAvailable.count++;
          counters.totalCreditsAvailable.matches.push(ticket.id);
        }
  
        if (['61272329', '32383830'].includes(pipelineStage) &&
            ['3612186226', '3658554544', '3632264778', '3653366158'].includes(productId)) {
          counters.extendedPlacementCredits.count++;
          counters.extendedPlacementCredits.matches.push(ticket.id);
        }
  
        if (pipeline === '11082157' && ['3652447404', '3299780235'].includes(productId)) {
          counters.totalCreditsPurchased.count++;
          counters.totalCreditsPurchased.matches.push(ticket.id);
        }
  
        // Deal-level counters
        if (pipelineStage === '61272329' && ['3299780235', '3294111583'].includes(productId)) {
          counters.dealCreditsAvailable.count++;
          counters.dealCreditsAvailable.matches.push(ticket.id);
        }
  
        if (pipeline === '11082157' && ['3299780235', '3294111583'].includes(productId)) {
          counters.dealCreditsPurchased.count++;
          counters.dealCreditsPurchased.matches.push(ticket.id);
        }
  
        const dealId = ticketDealMap[ticket.id];
        if (dealId) {
          if (!dealUpdates.has(dealId)) {
            dealUpdates.set(dealId, { creditsAvailable: 0, creditsPurchased: 0 });
          }
          
          const deal = dealUpdates.get(dealId);
          if (pipelineStage === '61272329' && ['3299780235', '3294111583'].includes(productId)) {
            deal.creditsAvailable++;
          }
          if (pipeline === '11082157' && ['3299780235', '3294111583'].includes(productId)) {
            deal.creditsPurchased++;
          }
        }
      });
  
      return dealUpdates;
    };
  
    const updateDeals = async (dealUpdates) => {
      const updatePromises = [];
      for (const [dealId, counts] of dealUpdates.entries()) {
        updatePromises.push(
          fetch(
            `https://api.hubapi.com/crm/v3/objects/deals/${dealId}`,
            {
              method: 'PATCH',
              headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                properties: {
                  credits_available: counts.creditsAvailable.toString(),
                  credits_purchased: counts.creditsPurchased.toString()
                }
              })
            }
          ).then(async response => {
            if (!response.ok) {
              throw new Error(`Error updating deal ${dealId}: ${await response.text()}`);
            }
            console.log(`Updated deal ${dealId}`);
          }).catch(error => {
            console.error(`Error updating deal ${dealId}:`, error);
          })
        );
      }
      await Promise.all(updatePromises);
    };
  
    try {
      let allDealUpdates = new Map();
      let after = undefined;
      let totalTickets = 0;
  
      do {
        const response = await fetch(
          `https://api.hubapi.com/crm/v3/objects/tickets/search`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              filterGroups: [{
                filters: [{
                  propertyName: 'associations.company',
                  operator: 'EQ',
                  value: companyId
                }]
              }],
              properties: ['hs_pipeline', 'hs_pipeline_stage', 'product_id_'],
              limit: 100,
              after
            })
          }
        );
  
        if (!response.ok) {
          throw new Error(`Error searching for tickets: ${await response.text()}`);
        }
  
        const searchData = await response.json();
        if (!searchData.results || searchData.results.length === 0) break;
  
        totalTickets += searchData.results.length;
        console.log(`Processing batch of ${searchData.results.length} tickets (total: ${totalTickets})`);
  
        const batchDealUpdates = await processTicketBatch(searchData.results);
        for (const [dealId, counts] of batchDealUpdates.entries()) {
          if (!allDealUpdates.has(dealId)) {
            allDealUpdates.set(dealId, { creditsAvailable: 0, creditsPurchased: 0 });
          }
          const existing = allDealUpdates.get(dealId);
          existing.creditsAvailable += counts.creditsAvailable;
          existing.creditsPurchased += counts.creditsPurchased;
        }
  
        after = searchData.paging?.next?.after;
      } while (after);
  
      // Update company properties
      const companyUpdateResponse = await fetch(
        `https://api.hubapi.com/crm/v3/objects/companies/${companyId}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            properties: {
              credits_pending: counters.totalCreditsAvailable.count.toString(),
              total_credits_purchased: counters.totalCreditsPurchased.count.toString(),
              extended_placement_credits: counters.extendedPlacementCredits.count.toString()
            }
          })
        }
      );
  
      if (!companyUpdateResponse.ok) {
        throw new Error(`Error updating company: ${await companyUpdateResponse.text()}`);
      }
  
      // Update deals
      await updateDeals(allDealUpdates);
  
      console.log('\n=== Final Summary ===');
      console.log(`Total tickets processed: ${totalTickets}`);
      console.log(`Company credits: Available=${counters.totalCreditsAvailable.count}, Purchased=${counters.totalCreditsPurchased.count}, Extended=${counters.extendedPlacementCredits.count}`);
      console.log(`Deals updated: ${allDealUpdates.size}`);
  
      sendResponse({
        message: `Successfully processed ${totalTickets} tickets, updated company credits and ${allDealUpdates.size} deals`
      });
    } catch (error) {
      console.error('Error:', error);
      sendResponse({
        message: 'Error occurred while processing',
        error: error.message
      });
    }
  };